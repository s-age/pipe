from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import CreateCompressorRequest
from pydantic import ValidationError


class CreateCompressorSessionAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        try:
            request_data = CreateCompressorRequest(**self.request_data.get_json())

            result = session_service.run_takt_for_compression(
                request_data.session_id,
                request_data.policy,
                request_data.target_length,
                request_data.start_turn,
                request_data.end_turn,
            )

            return result, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500


class ApproveCompressorAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        try:
            session_id = self.params.get("session_id")
            if not session_id:
                return {"message": "session_id is required"}, 400

            # session_serviceの承認メソッドを呼び出す
            session_service.approve_compression(session_id)

            return {"message": "Compression approved"}, 200

        except Exception as e:
            return {"message": str(e)}, 500


class DenyCompressorAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        try:
            session_id = self.params.get("session_id")
            if not session_id:
                return {"message": "session_id is required"}, 400

            # session_serviceの拒否メソッドを呼び出す
            session_service.deny_compression(session_id)

            return {}, 204

        except Exception as e:
            return {"message": str(e)}, 500
