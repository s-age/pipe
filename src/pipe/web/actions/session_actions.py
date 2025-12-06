import json
import os
import subprocess
import sys
from typing import Any

from flask import Response, stream_with_context
from pipe.core.models.turn import Turn
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pydantic import ValidationError


class SessionStartAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        try:
            request_data = StartSessionRequest(**self.request_data.get_json())

            session = get_session_service().create_new_session(
                purpose=request_data.purpose,
                background=request_data.background,
                roles=request_data.roles,
                multi_step_reasoning_enabled=request_data.multi_step_reasoning_enabled,
                hyperparameters=request_data.hyperparameters,
                parent_id=request_data.parent,
                artifacts=request_data.artifacts,
                procedure=request_data.procedure,
            )
            session_id = session.session_id

            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                session_id,
                "--instruction",
                request_data.instruction,
                "--output-format",
                "stream-json",
            ]
            if request_data.references:
                command.extend(
                    ["--references", ",".join(r.path for r in request_data.references)]
                )
            if request_data.artifacts:
                command.extend(["--artifacts", ",".join(request_data.artifacts)])
            if request_data.procedure:
                command.extend(["--procedure", request_data.procedure])
            if request_data.multi_step_reasoning_enabled:
                command.append("--multi-step-reasoning")

            subprocess.run(
                command, capture_output=True, text=True, check=True, encoding="utf-8"
            )

            return {"session_id": session_id}, 200

        except ValidationError as e:
            # Log the invalid payload so we can inspect submitted hyperparameters
            try:
                payload = (
                    self.request_data.get_json()
                    if self.request_data is not None
                    else None
                )
                print(
                    f"DEBUG: StartSession validation failed. Payload: {payload}",
                    file=sys.stderr,
                )
            except Exception:
                pass
            return {"message": str(e)}, 422
        except subprocess.CalledProcessError as e:
            return {
                "message": (
                    "Conductor script failed during initial instruction processing."
                ),
                "details": e.stderr,
            }, 500
        except Exception as e:
            return {"message": str(e)}, 500


class SessionGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            session_data = get_session_service().get_session(session_id)
            if not session_data:
                return {"message": "Session not found."}, 404

            return {"session": session_data.to_dict()}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class SessionDeleteAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            get_session_service().delete_session(session_id)
            return {"message": f"Session {session_id} deleted."}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class SessionRawAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            repo = get_session_service().repository
            session_path = repo._get_path_for_id(session_id)
            exists = os.path.exists(session_path)
            result: dict = {
                "computed_path": session_path,
                "sessions_dir": repo.sessions_dir,
                "exists": exists,
            }

            if exists:
                with open(session_path) as f:
                    data = json.load(f)
                result["file"] = data
                return result, 200

            backups_dir = getattr(
                repo, "backups_dir", os.path.join(repo.sessions_dir, "backups")
            )
            matches = []
            if os.path.isdir(backups_dir):
                for name in os.listdir(backups_dir):
                    path = os.path.join(backups_dir, name)
                    try:
                        with open(path) as bf:
                            bd = json.load(bf)
                            if bd.get("session_id") == session_id:
                                matches.append({"backup_file": path, "content": bd})
                    except Exception:
                        continue

            result["backups_found"] = len(matches)
            if matches:
                matches_sorted = sorted(
                    matches,
                    key=lambda m: os.path.getmtime(m["backup_file"]),
                    reverse=True,
                )
                result["latest_backup"] = matches_sorted[0]

            return result, 404
        except Exception as e:
            return {"message": str(e)}, 500


class SessionInstructionAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any] | Response, int]:
        from pipe.web.service_container import get_session_service, get_settings

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            request_data = SendInstructionRequest(**self.request_data.get_json())
            instruction = request_data.instruction

            session_data = get_session_service().get_session(session_id)
            if not session_data:
                return {"message": "Session not found."}, 404

            if session_data.pools and len(session_data.pools) >= 7:
                error_message = (
                    "Too many tasks in the processing pool (limit is 7). "
                    "Please wait for the current tasks to complete before "
                    "adding a new one."
                )

                def error_generate():
                    yield f"data: {json.dumps({'error': error_message})}\n\n"

                return (
                    Response(
                        stream_with_context(error_generate()),
                        mimetype="text/event-stream",
                        status=400,
                    ),
                    400,
                )

            enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

            response = None
            settings = get_settings()
            if settings.api_mode == "gemini-api":
                # For gemini-api, stream directly without subprocess
                from pipe.core.agents import get_agent_class
                from pipe.core.factories.service_factory import ServiceFactory

                session_service = get_session_service()
                service_factory = ServiceFactory(session_service.project_root, settings)
                prompt_service = service_factory.create_prompt_service()

                # Prepare args-like object
                args = type(
                    "Args",
                    (),
                    {
                        "instruction": instruction,
                        "output_format": "stream-json",
                        "dry_run": False,
                        "session": session_id,
                        "references": [],
                        "references_persist": [],
                        "artifacts": [],
                        "purpose": None,
                        "background": None,
                        "roles": [],
                        "parent": None,
                        "procedure": None,
                        "multi_step_reasoning": enable_multi_step_reasoning,
                        "fork": None,
                        "at_turn": None,
                        "api_mode": None,
                    },
                )()

                # Prepare session
                session_service.prepare(args, is_dry_run=False)

                # Get agent from registry
                AgentClass = get_agent_class(settings.api_mode)
                agent = AgentClass()

                def generate():
                    token_count = 0
                    turns_to_save: list[Turn] = []
                    try:
                        for item in agent.run_stream(args, session_service, prompt_service):
                            if (
                                isinstance(item, tuple)
                                and len(item) == 4
                                and item[0] == "end"
                            ):
                                end, _, token_count, turns_to_save = item
                                # After streaming, add turns
                                for turn in turns_to_save:
                                    get_session_service().add_turn_to_session(
                                        session_id, turn
                                    )
                                if token_count is not None:
                                    get_session_service().update_token_count(
                                        session_id, token_count
                                    )
                                yield (f"data: {json.dumps({'end': True})}\n\n")
                            else:
                                # Ensure item is a string before JSON dumping
                                content = (
                                    item.decode("utf-8")
                                    if isinstance(item, bytes)
                                    else item
                                )
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                response = (
                    Response(
                        stream_with_context(generate()), mimetype="text/event-stream"
                    ),
                    200,
                )
            else:
                # For gemini-cli, use subprocess
                command = [
                    sys.executable,
                    "-m",
                    "pipe.cli.takt",
                    "--session",
                    session_id,
                    "--instruction",
                    instruction,
                    "--output-format",
                    "stream-json",
                ]
                if enable_multi_step_reasoning:
                    command.append("--multi-step-reasoning")

                def generate():
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        bufsize=1,
                    )

                    if process.stdout:
                        for line in iter(process.stdout.readline, ""):
                            yield f"data: {json.dumps({'content': line})}\n\n"
                        process.stdout.close()

                    stderr_output = ""
                    if process.stderr:
                        stderr_output = process.stderr.read()
                        process.stderr.close()

                    return_code = process.wait()

                    if return_code != 0:
                        yield f"data: {json.dumps({'error': stderr_output})}\n\n"

                response = (
                    Response(
                        stream_with_context(generate()), mimetype="text/event-stream"
                    ),
                    200,
                )

            return response
        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500


class SessionForkAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        fork_index = self.params.get("fork_index")
        if fork_index is None:
            return {"message": "fork_index is required"}, 400

        try:
            fork_index = int(fork_index)
        except ValueError:
            return {"message": "fork_index must be an integer"}, 400

        try:
            session_id = self.params.get("session_id")
            if not session_id:
                return {"message": "session_id is required"}, 400

            new_session_id = get_session_service().fork_session(session_id, fork_index)
            if new_session_id:
                return {"new_session_id": new_session_id}, 200
            else:
                return {"message": "Failed to fork session."}, 500

        except ValidationError as e:
            return {"message": str(e)}, 422
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except IndexError:
            return {"message": "Fork turn index out of range."}, 400
        except Exception as e:
            return {"message": str(e)}, 500
