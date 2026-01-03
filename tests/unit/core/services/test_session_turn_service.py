from datetime import UTC, datetime
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
from pipe.core.models.turn import ModelResponseTurnUpdate, UserTaskTurnUpdate
from pipe.core.services.session_turn_service import SessionTurnService

from tests.factories.models import SessionFactory, TurnFactory, create_test_settings


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_settings():
    settings = create_test_settings()
    settings.timezone = "Asia/Tokyo"
    settings.tool_response_expiration = 3
    return settings


@pytest.fixture
def service(mock_settings, mock_repository):
    return SessionTurnService(settings=mock_settings, repository=mock_repository)


class TestSessionTurnServiceInit:
    def test_init_valid_timezone(self, mock_settings, mock_repository):
        mock_settings.timezone = "UTC"
        service = SessionTurnService(mock_settings, mock_repository)
        assert service.timezone == ZoneInfo("UTC")

    def test_init_invalid_timezone_fallback_to_utc(
        self, mock_settings, mock_repository
    ):
        mock_settings.timezone = "Invalid/Timezone"
        service = SessionTurnService(mock_settings, mock_repository)
        assert service.timezone == ZoneInfo("UTC")


class TestSessionTurnServiceDeleteTurn:
    def test_delete_turn_success(self, service, mock_repository):
        session = SessionFactory.create_with_turns(turn_count=3)
        mock_repository.find.return_value = session

        # Mock delete_by_index
        session.turns.delete_by_index = Mock()

        service.delete_turn("test-session", 1)

        session.turns.delete_by_index.assert_called_once_with(1)
        mock_repository.save.assert_called_once_with(session)

    def test_delete_turn_session_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        with pytest.raises(
            FileNotFoundError, match="Session with ID 'test-session' not found"
        ):
            service.delete_turn("test-session", 0)


class TestSessionTurnServiceDeleteTurns:
    @patch("pipe.core.services.session_turn_service.delete_turns")
    def test_delete_turns_success(
        self, mock_delete_turns_domain, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session

        indices = [0, 2]
        service.delete_turns("test-session", indices)

        mock_delete_turns_domain.assert_called_once_with(session, indices)
        mock_repository.save.assert_called_once_with(session)

    def test_delete_turns_session_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        with pytest.raises(
            FileNotFoundError, match="Session with ID 'test-session' not found"
        ):
            service.delete_turns("test-session", [0])


class TestSessionTurnServiceEditTurn:
    def test_edit_turn_user_task_dict(self, service, mock_repository):
        session = SessionFactory.create()
        turn = TurnFactory.create_user_task(instruction="Old")
        session.turns.add(turn)
        mock_repository.find.return_value = session

        session.turns.edit_by_index = Mock()

        new_data = {"instruction": "New"}
        service.edit_turn("test-session", 0, new_data)

        # Verify conversion to DTO
        args, _ = session.turns.edit_by_index.call_args
        assert isinstance(args[1], UserTaskTurnUpdate)
        assert args[1].instruction == "New"
        mock_repository.save.assert_called_once_with(session)

    def test_edit_turn_model_response_dict(self, service, mock_repository):
        session = SessionFactory.create()
        turn = TurnFactory.create_model_response(content="Old")
        session.turns.add(turn)
        mock_repository.find.return_value = session

        session.turns.edit_by_index = Mock()

        new_data = {"content": "New"}
        service.edit_turn("test-session", 0, new_data)

        args, _ = session.turns.edit_by_index.call_args
        assert isinstance(args[1], ModelResponseTurnUpdate)
        assert args[1].content == "New"

    def test_edit_turn_with_dto(self, service, mock_repository):
        session = SessionFactory.create()
        turn = TurnFactory.create_user_task()
        session.turns.add(turn)
        mock_repository.find.return_value = session

        session.turns.edit_by_index = Mock()

        update_dto = UserTaskTurnUpdate(instruction="New")
        service.edit_turn("test-session", 0, update_dto)

        session.turns.edit_by_index.assert_called_once_with(0, update_dto)

    def test_edit_turn_session_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        with pytest.raises(
            FileNotFoundError, match="Session with ID 'test-session' not found"
        ):
            service.edit_turn("test-session", 0, {})

    def test_edit_turn_index_out_of_range(self, service, mock_repository):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        with pytest.raises(IndexError, match="Turn index out of range"):
            service.edit_turn("test-session", 0, {})

    def test_edit_turn_invalid_type(self, service, mock_repository):
        session = SessionFactory.create()
        # Create a turn type that is not user_task or model_response
        mock_turn = Mock()
        mock_turn.type = "function_calling"
        session.turns.add(mock_turn)
        mock_repository.find.return_value = session

        with pytest.raises(
            ValueError, match="Editing turns of type 'function_calling' is not allowed"
        ):
            service.edit_turn("test-session", 0, {"some": "data"})

    def test_edit_turn_validation_error(self, service, mock_repository):
        session = SessionFactory.create()
        turn = TurnFactory.create_user_task()
        session.turns.add(turn)
        mock_repository.find.return_value = session

        with pytest.raises(ValueError, match="Invalid turn update data"):
            # Passing an extra field should fail validation as extra="forbid"
            service.edit_turn("test-session", 0, {"extra_field": "value"})


class TestSessionTurnServiceAddTurn:
    def test_add_turn_to_session_success(self, service, mock_repository):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        turn = TurnFactory.create_user_task()

        session.turns.add = Mock()

        service.add_turn_to_session("test-session", turn)

        session.turns.add.assert_called_once_with(turn)
        mock_repository.save.assert_called_once_with(session)

    def test_add_turn_to_session_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        service.add_turn_to_session("test-session", TurnFactory.create_user_task())
        mock_repository.save.assert_not_called()


class TestSessionTurnServicePoolOperations:
    @patch("pipe.core.collections.turns.TurnCollection")
    def test_merge_pool_into_turns_success(
        self, mock_turn_collection_cls, service, mock_repository
    ):
        session = SessionFactory.create()
        original_pools = Mock()
        session.pools = original_pools
        mock_repository.find.return_value = session

        session.turns.merge_from = Mock()
        empty_collection = Mock()
        mock_turn_collection_cls.return_value = empty_collection

        service.merge_pool_into_turns("test-session")

        session.turns.merge_from.assert_called_once_with(original_pools)
        assert session.pools == empty_collection
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.services.session_turn_service.PoolCollection.add")
    def test_add_to_pool_success(self, mock_pool_add, service, mock_repository):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        turn = TurnFactory.create_user_task()

        service.add_to_pool("test-session", turn)

        mock_pool_add.assert_called_once_with(session, turn)
        mock_repository.save.assert_called_once_with(session)

    def test_get_pool_success(self, service, mock_repository):
        session = SessionFactory.create()
        session.pools = [TurnFactory.create_user_task()]
        mock_repository.find.return_value = session

        result = service.get_pool("test-session")
        assert result == session.pools

    def test_get_pool_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        assert service.get_pool("test-session") == []

    @patch("pipe.core.services.session_turn_service.PoolCollection.get_and_clear")
    def test_get_and_clear_pool_success(
        self, mock_get_and_clear, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        expected_turns = [TurnFactory.create_user_task()]
        mock_get_and_clear.return_value = expected_turns

        result = service.get_and_clear_pool("test-session")

        assert result == expected_turns
        mock_get_and_clear.assert_called_once_with(session)
        mock_repository.save.assert_called_once_with(session)

    def test_get_and_clear_pool_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        assert service.get_and_clear_pool("test-session") == []


class TestSessionTurnServiceExpireOldToolResponses:
    @patch("pipe.core.services.session_turn_service.expire_old_tool_responses")
    def test_expire_old_tool_responses_success(
        self, mock_expire_domain, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        mock_expire_domain.return_value = True  # Changes made

        service.expire_old_tool_responses("test-session")

        mock_expire_domain.assert_called_once_with(
            session.turns, service.settings.tool_response_expiration
        )
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.services.session_turn_service.expire_old_tool_responses")
    def test_expire_old_tool_responses_no_changes(
        self, mock_expire_domain, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        mock_expire_domain.return_value = False

        service.expire_old_tool_responses("test-session")
        mock_repository.save.assert_not_called()


class TestSessionTurnServiceUpdateRawResponse:
    def test_update_raw_response_success(self, service, mock_repository):
        session = SessionFactory.create()
        mock_repository.find.return_value = session

        service.update_raw_response("test-session", "new response")

        assert session.raw_response == "new response"
        mock_repository.save.assert_called_once_with(session)


class TestSessionTurnServiceTransactions:
    @freeze_time("2025-01-01 12:00:00")
    @patch("pipe.core.services.session_turn_service.PoolCollection.add")
    @patch("pipe.core.models.turn.UserTaskTurn")
    @patch("pipe.core.utils.datetime.get_current_timestamp")
    def test_start_transaction_success(
        self, mock_get_ts, mock_user_turn_cls, mock_pool_add, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session

        ts = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        mock_get_ts.return_value = ts

        mock_turn = Mock()
        mock_user_turn_cls.return_value = mock_turn

        result = service.start_transaction("test-session", "instruction")

        assert result == session
        mock_user_turn_cls.assert_called_once_with(
            type="user_task", instruction="instruction", timestamp=ts
        )
        mock_pool_add.assert_called_once_with(session, mock_turn)
        mock_repository.save.assert_called_once_with(session)

    def test_start_transaction_not_found(self, service, mock_repository):
        mock_repository.find.return_value = None
        with pytest.raises(ValueError, match="Session test-session not found"):
            service.start_transaction("test-session", "instruction")

    @patch("pipe.core.services.session_turn_service.PoolCollection.add")
    def test_add_to_transaction_success(self, mock_pool_add, service, mock_repository):
        session = SessionFactory.create()
        mock_repository.find.return_value = session
        turn = TurnFactory.create_model_response()

        service.add_to_transaction("test-session", turn)

        mock_pool_add.assert_called_once_with(session, turn)
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.collections.turns.TurnCollection")
    def test_commit_transaction_success(
        self, mock_turn_collection_cls, service, mock_repository
    ):
        session = SessionFactory.create()
        original_pools = Mock()
        session.pools = original_pools
        mock_repository.find.return_value = session

        session.turns.merge_from = Mock()
        empty_collection = Mock()
        mock_turn_collection_cls.return_value = empty_collection

        service.commit_transaction("test-session")

        session.turns.merge_from.assert_called_once_with(original_pools)
        assert session.pools == empty_collection
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.collections.turns.TurnCollection")
    def test_rollback_transaction_success(
        self, mock_turn_collection_cls, service, mock_repository
    ):
        session = SessionFactory.create()
        mock_repository.find.return_value = session

        empty_collection = Mock()
        mock_turn_collection_cls.return_value = empty_collection

        service.rollback_transaction("test-session")

        assert session.pools == empty_collection
        mock_repository.save.assert_called_once_with(session)
