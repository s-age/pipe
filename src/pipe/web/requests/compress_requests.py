from pydantic import BaseModel, field_validator


class CreateCompressorRequest(BaseModel):
    session_id: str
    policy: str
    target_length: int
    start_turn: int
    end_turn: int

    @field_validator("start_turn", "end_turn")
    @classmethod
    def validate_turns(cls, v, info):
        # In the API we accept 1-based turn numbers. Validate they are >= 1.
        if v < 1:
            raise ValueError("Turn number must be >= 1")
        return v

    @field_validator("end_turn")
    @classmethod
    def validate_turn_range(cls, v, info):
        start_turn = info.data.get("start_turn")
        if start_turn is not None and v < start_turn:
            raise ValueError("end_turn must be greater than or equal to start_turn")
        return v

    @field_validator("session_id")
    @classmethod
    def validate_session_exists(cls, v, info):
        from pipe.web.app import session_service

        session = session_service.get_session(v)
        if not session:
            raise ValueError("Session not found")
        info.data["session"] = session  # Store session for later use
        return v

    @field_validator("start_turn", "end_turn")
    @classmethod
    def validate_turn_exists(cls, v, info):
        session = info.data.get("session")
        if session:
            # `v` is 1-based here; valid range is 1..len(session.turns)
            if v > len(session.turns):
                raise ValueError(f"Turn {v} does not exist in session")
        return v
