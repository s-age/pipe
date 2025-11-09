import json
import os
import subprocess
import sys
from typing import Any

from flask import Response, stream_with_context
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.fork_session import ForkSessionRequest
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pydantic import ValidationError


class SessionStartAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        try:
            request_data = StartSessionRequest(**self.request_data.get_json())

            session = session_service.create_new_session(
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
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            session_data = session_service.get_session(session_id)
            if not session_data:
                return {"message": "Session not found."}, 404

            return {"session": session_data.to_dict()}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class SessionDeleteAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            session_service.delete_session(session_id)
            return {"message": f"Session {session_id} deleted."}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class SessionRawAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            repo = session_service.repository
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
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            request_data = SendInstructionRequest(**self.request_data.get_json())
            instruction = request_data.instruction

            session_data = session_service.get_session(session_id)
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

                return Response(
                    stream_with_context(error_generate()),
                    mimetype="text/event-stream",
                    status=400,
                ), 400

            enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                session_id,
                "--instruction",
                instruction,
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

            return (
                Response(stream_with_context(generate()), mimetype="text/event-stream"),
                200,
            )
        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500


class SessionForkAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        fork_index = self.params.get("fork_index")
        if fork_index is None:
            return {"message": "fork_index is required"}, 400

        try:
            fork_index = int(fork_index)
        except ValueError:
            return {"message": "fork_index must be an integer"}, 400

        try:
            request_data = ForkSessionRequest(**self.request_data.get_json())
            session_id = request_data.session_id

            new_session_id = session_service.fork_session(session_id, fork_index)
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
