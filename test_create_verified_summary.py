import sys

sys.path.insert(0, "/Users/s-age/gitrepos/pipe/src")

from pipe.core.models.settings import Settings
from pipe.core.services.session_service import SessionService
from pipe.core.tools.create_verified_summary import create_verified_summary

# Mock settings and session_service
settings = Settings(
    api_mode="gemini-cli",  # or "gemini-api"
    model="gemini-1.5-flash",
    timezone="Asia/Tokyo",
    parameters=None,
)

session_service = SessionService(
    project_root="/Users/s-age/gitrepos/pipe",
    settings=settings,
    repository=None,  # Mock
)

# Test call 1: missing session_id
try:
    result = create_verified_summary(
        start_turn=1,
        end_turn=5,
        policy="Test policy",
        target_length=1000,
        settings=settings,
        project_root="/Users/s-age/gitrepos/pipe",
        session_service=session_service,
    )
    print("Test 1 result:", result)
except Exception as e:
    print("Test 1 error:", e)

# Test call 2: missing session_id
try:
    result = create_verified_summary(
        start_turn=31,
        end_turn=39,
        policy="Test policy",
        target_length=1000,
        settings=settings,
        project_root="/Users/s-age/gitrepos/pipe",
        session_service=session_service,
    )
    print("Test 2 result:", result)
except Exception as e:
    print("Test 2 error:", e)

# Test call 3: with session_id
try:
    result = create_verified_summary(
        session_id="ff7cd29a70fa0929c6dbe91967bac28ce05709704900852826208c54133b36ed",
        start_turn=31,
        end_turn=39,
        policy="Test policy",
        target_length=1000,
        settings=settings,
        project_root="/Users/s-age/gitrepos/pipe",
        session_service=session_service,
    )
    print("Test 3 result:", result)
except Exception as e:
    print("Test 3 error:", e)
