"""Result models for ts_checker tool."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class CommandCheckResult(CamelCaseModel):
    """Result from running a single check command (lint or build)."""

    errors: list[str] = Field(
        default_factory=list, description="List of error messages"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of warning messages"
    )


class TSCheckerResult(CamelCaseModel):
    """Result from running TypeScript lint and build checks."""

    lint: CommandCheckResult | None = Field(
        default=None, description="Lint check results"
    )
    build: CommandCheckResult | None = Field(
        default=None, description="Build check results"
    )
