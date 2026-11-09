"""Regression tests for legacy Envoy-R compatibility."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.enphase_gateway.gateway_reader.auth import LegacyAuth
from custom_components.enphase_gateway.gateway_reader.gateway import EnvoyLegacy
from custom_components.enphase_gateway.gateway_reader.gateway_reader import (
    EnvoyUtils,
    GatewayReader,
)


def legacy_reader(serial_number="121137057297"):
    """Return a prepared-enough reader for legacy authentication tests."""
    reader = GatewayReader("127.0.0.1", async_client=MagicMock())
    reader._info.populated = True
    reader._info.web_tokens = False
    reader._info.serial_number = serial_number
    return reader


@pytest.mark.asyncio
async def test_envoy_legacy_auth_uses_last_six_serial_digits():
    """Blank envoy password should use the last six serial-number digits."""
    reader = legacy_reader()

    await reader.authenticate(username="envoy", password=None)

    assert isinstance(reader.auth, LegacyAuth)
    assert reader.auth._username == "envoy"
    assert reader.auth._password == "057297"


@pytest.mark.asyncio
async def test_installer_legacy_auth_uses_generated_password(monkeypatch):
    """Blank installer password should use EnvoyUtils password generation."""
    reader = legacy_reader()
    monkeypatch.setattr(
        EnvoyUtils,
        "get_password",
        lambda serial_number, username: "generated-password",
    )

    await reader.authenticate(username="installer", password=None)

    assert isinstance(reader.auth, LegacyAuth)
    assert reader.auth._username == "installer"
    assert reader.auth._password == "generated-password"


@pytest.mark.asyncio
async def test_legacy_endpoint_uses_extended_timeout():
    """Legacy HTML endpoints should get more than the default 10 seconds."""
    reader = GatewayReader("127.0.0.1", async_client=MagicMock())
    reader.auth = LegacyAuth(reader.host, "envoy", "password")
    reader.gateway = EnvoyLegacy()
    reader.gateway.set_endpoint_data = MagicMock()
    reader._async_get = AsyncMock(return_value="response")

    endpoint = MagicMock()
    endpoint.get_url.return_value = "http://127.0.0.1/production"

    await reader._update_endpoint(endpoint)

    reader._async_get.assert_awaited_once_with(
        "http://127.0.0.1/production",
        follow_redirects=False,
        timeout=30.0,
    )
