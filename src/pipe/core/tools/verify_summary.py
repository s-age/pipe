from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationOutput,
)
from pipe.core.models.settings import Settings


def verify_summary(
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary_text: str,
    settings: Settings,
    project_root: str,
    session_service=None,
) -> VerificationOutput:
    """
    Verifies a summary by creating a new temporary session for a sub-agent,
    and returns the verification status and the ID of the temporary session.

    Returns:
        VerificationResult on success, VerificationError on failure
    """
    # NOTE: session_service argument is preserved for compatibility but not
    # used directly for the main logic to ensure service independence.

    try:
        factory = ServiceFactory(project_root, settings)
        verification_service = factory.create_verification_service()

        return verification_service.verify_summary(
            session_id, start_turn, end_turn, summary_text
        )
    except Exception as e:
        import traceback

        return VerificationError(
            error=(
                "An unexpected error occurred during summary verification: "
                f"{e}\n{traceback.format_exc()}"
            )
        )
