#!/usr/bin/env python3

import json
from unittest.mock import Mock, patch

from pipe.web.actions.compress_actions import CreateCompressorSessionAction

# Mock request data
mock_request = Mock()
mock_request.get_json.return_value = {
    "session_id": "e6553452636ca8e56a4049f764ad7536272f47a59f8392d66cddf2bc734d134b",
    "policy": "会話の趣旨とどの様な応答があったか",
    "target_length": 500,
    "start_turn": 5,
    "end_turn": 13,
}

# Create action instance
action = CreateCompressorSessionAction(params={}, request_data=mock_request)

# Mock the service method
with patch("pipe.web.app.session_service.run_takt_for_compression") as mock_run:
    mock_run.return_value = "mocked_session_id"

    # Execute
    response_data, status_code = action.execute()

print(f"Status Code: {status_code}")
print(f"Response: {json.dumps(response_data, indent=2)}")
