import json
import subprocess
import sys
from typing import TypedDict

from flask import Response, stream_with_context
from pipe.core.models.turn import Turn
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pipe.web.requests.sessions.start_session import StartSessionRequest


class SessionData(TypedDict, total=False):
    session_id: str
    created_at: str
    purpose: str
    background: str
    roles: str
    multi_step_reasoning_enabled: bool
    token_count: int
    hyperparameters: dict | None
    references: list[dict]
    artifacts: list[str]
    procedure: str | None
    turns: list[dict]
    pools: list[dict]
    todos: list[dict]


class SessionStartAction(BaseAction):
    body_model = StartSessionRequest  # Legacy pattern: no path params

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

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

        return {"session_id": session_id}


class SessionGetAction(BaseAction):
    def execute(self) -> SessionData:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        session_data = get_session_service().get_session(session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        # Return SessionData directly (dispatcher will wrap in {success, data})
        return session_data.to_dict()


class SessionDeleteAction(BaseAction):
    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        get_session_service().delete_session(session_id)
        return {"message": f"Session {session_id} deleted."}


class SessionInstructionAction(BaseAction):
    request_model = SendInstructionRequest

    def execute(self) -> Response:
        """
        Returns a Flask Response object with streaming content.
        This action is special and should be handled by streaming_dispatcher.
        """
        from pipe.web.service_container import get_session_service, get_settings

        request = self.validated_request
        instruction = request.instruction

        session_data = get_session_service().get_session(request.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        if session_data.pools and len(session_data.pools) >= 7:
            error_message = (
                "Too many tasks in the processing pool (limit is 7). "
                "Please wait for the current tasks to complete before "
                "adding a new one."
            )

            def error_generate():
                yield f"data: {json.dumps({'error': error_message})}\n\n"

            raise BadRequestError(error_message)

        enable_multi_step_reasoning = session_data.multi_step_reasoning_enabled

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
                    "session": request.session_id,
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
                                    request.session_id, turn
                                )
                            if token_count is not None:
                                get_session_service().update_token_count(
                                    request.session_id, token_count
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

            return Response(
                stream_with_context(generate()), mimetype="text/event-stream"
            )
        else:
            # For gemini-cli, use subprocess
            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                request.session_id,
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

            return Response(
                stream_with_context(generate()), mimetype="text/event-stream"
            )
