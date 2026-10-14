"""Behavior protected while making the legacy code pass static type checks."""

from unittest.mock import AsyncMock

import httpx
import pytest

from pymyenergi.connection import Connection
from pymyenergi.zappi import Zappi


@pytest.mark.parametrize(
    "username,password", [(None, "key"), ("hub", None), (None, None)]
)
def test_missing_hub_credentials_fail_without_network(username, password):
    transport = AsyncMock()
    with pytest.raises(TypeError, match="Hub serial number and API key"):
        Connection(username, password, asyncClient=transport)
    transport.request.assert_not_called()
    transport.get.assert_not_called()


@pytest.mark.parametrize("username,password", [("hub", "key"), ("", "")])
def test_present_credentials_keep_digest_auth_without_network(username, password):
    transport = AsyncMock()
    connection = Connection(username, password, asyncClient=transport)
    assert isinstance(connection.auth, httpx.DigestAuth)
    transport.request.assert_not_called()
    transport.get.assert_not_called()


def test_data_setter_still_recomputes_ct_groups():
    device = Zappi(AsyncMock(), 16042300, {"ectt1": "Grid", "ectp1": 10})
    assert device.ct_groups == {"ct_grid": 10}
    replacement = {"ectt1": "Grid", "ectp1": 25}
    device.data = replacement
    assert device.data is replacement
    assert device.ct_groups == {"ct_grid": 25}
