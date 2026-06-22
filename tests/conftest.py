"""Common fixtures  for the Philips Hue Play HDMI Sync Box integration tests."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations) -> Generator[None]:  # noqa: ANN001, ARG001
    """Enable custom integrations."""
    yield  # noqa: PT022


# Copied from HA tests/components/conftest.py
@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Test fixture that ensures all entities are enabled in the registry."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        return_value=True,
    ):
        yield
