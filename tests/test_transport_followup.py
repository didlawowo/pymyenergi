"""Solar-priority transport, parsing and CLI regressions; strictly offline."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from pymyenergi import LIBBI
from pymyenergi import ZAPPI
from pymyenergi.cli import main
from pymyenergi.client import MyenergiClient
from pymyenergi.connection import Connection
from pymyenergi.exceptions import MyenergiException
from pymyenergi.exceptions import TimeoutException
from pymyenergi.exceptions import WrongCredentials
from pymyenergi.libbi import Libbi
from pymyenergi.zappi import Zappi


@pytest.mark.asyncio
async def test_owned_clients_are_independent_and_context_managed():
    async with Connection("hub", "key") as first:
        async with Connection("hub", "key") as second:
            assert first.asyncClient is not second.asyncClient
            await first.aclose()
            await first.aclose()
            assert first.asyncClient.is_closed
            assert not second.asyncClient.is_closed
        assert second.asyncClient.is_closed


@pytest.mark.asyncio
async def test_injected_client_remains_owned_by_the_caller():
    async with httpx.AsyncClient() as transport:
        async with Connection("hub", "key", asyncClient=transport) as connection:
            assert connection.asyncClient is transport
        assert not transport.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("at_discovery", [True, False])
@pytest.mark.parametrize("status", [401, 403, 429, 500, 503])
async def test_http_status_is_not_misreported_as_missing_credentials(
    at_discovery, status
):
    transport = AsyncMock(spec=httpx.AsyncClient)
    transport.get.return_value = httpx.Response(status, json={})
    transport.request.return_value = httpx.Response(status, json={})
    connection = Connection("hub", "key", asyncClient=transport)
    if not at_discovery:
        connection.base_url = "https://s18.myenergi.net"
        connection.do_query_asn = False
    expected = WrongCredentials if status == 401 else MyenergiException
    with pytest.raises(expected) as caught:
        await connection.get("/cgi-jstatus-Z123")
    if status != 401:
        assert not isinstance(caught.value, WrongCredentials)
        assert caught.value.code == status
        assert str(caught.value)
        assert connection.do_query_asn


@pytest.mark.asyncio
async def test_known_server_does_not_require_asn_on_every_successful_response():
    transport = AsyncMock(spec=httpx.AsyncClient)
    transport.request.return_value = httpx.Response(200, json={"ok": True})
    connection = Connection("hub", "key", asyncClient=transport)
    connection.base_url = "https://s18.myenergi.net"
    connection.do_query_asn = False
    assert await connection.get("/cgi-jstatus-Z123") == {"ok": True}
    assert connection.base_url == "https://s18.myenergi.net"
    transport.get.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_discovery_header_is_a_protocol_error_not_an_auth_claim():
    transport = AsyncMock(spec=httpx.AsyncClient)
    transport.get.return_value = httpx.Response(200, json={})
    connection = Connection("hub", "key", asyncClient=transport)
    with pytest.raises(MyenergiException) as caught:
        await connection.get("/cgi-jstatus-Z123")
    assert not isinstance(caught.value, WrongCredentials)
    transport.request.assert_not_awaited()
    assert connection.do_query_asn


@pytest.mark.asyncio
@pytest.mark.parametrize("oauth", [False, True])
@pytest.mark.parametrize(
    "kind",
    [httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout],
)
async def test_all_request_timeouts_keep_their_cause_without_automatic_retry(
    oauth, kind
):
    transport = AsyncMock(spec=httpx.AsyncClient)
    failure = kind("simulated timeout")
    transport.request.side_effect = failure
    connection = Connection("hub", "key", asyncClient=transport)
    connection.base_url = "https://s18.myenergi.net"
    connection.do_query_asn = False
    if oauth:
        connection.app_email = "offline@example.invalid"
        connection.app_password = "offline"
        connection.oauth_headers = {"Authorization": "Bearer offline"}
    with pytest.raises(TimeoutException) as caught:
        await connection.get("/offline", oauth=oauth)
    assert caught.value.__cause__ is failure
    assert transport.request.await_count == 1
    if not oauth:
        assert connection.do_query_asn


@pytest.mark.asyncio
async def test_oauth_without_credentials_cannot_silently_return_none():
    transport = AsyncMock(spec=httpx.AsyncClient)
    connection = Connection("hub", "key", asyncClient=transport)
    with pytest.raises(WrongCredentials):
        await connection.get("/api/Location", oauth=True)
    transport.request.assert_not_awaited()


@pytest.mark.parametrize("value", [-1, 99, None, "3", True, [], {}])
@pytest.mark.parametrize(
    "key,property_name", [("sta", "status"), ("zmo", "charge_mode")]
)
def test_unknown_enum_values_do_not_crash_or_invent_a_valid_state(
    value, key, property_name
):
    device = Zappi(AsyncMock(spec=Connection), 123, {key: value})
    assert getattr(device, property_name) == "Unknown"


@pytest.mark.parametrize(
    "level", [-1, 101, True, 1.5, None, "-1", "101", "nan", [], {}]
)
@pytest.mark.asyncio
async def test_invalid_green_levels_fail_before_network(level):
    transport = AsyncMock(spec=Connection)
    device = Zappi(transport, 123, {"mgl": 50})
    with pytest.raises(ValueError):
        await device.set_minimum_green_level(level)
    transport.get.assert_not_awaited()
    assert device.minimum_green_level == 50


@pytest.mark.parametrize(
    "level,expected", [(0, 0), (100, 100), (50, 50), ("0", 0), ("100", 100)]
)
@pytest.mark.asyncio
async def test_valid_green_levels_preserve_cli_string_support(level, expected):
    transport = AsyncMock(spec=Connection)
    device = Zappi(transport, 123)
    await device.set_minimum_green_level(level)
    transport.get.assert_awaited_once_with(f"/cgi-set-min-green-Z123-{expected}")
    assert device.minimum_green_level == expected


def test_configured_serial_is_available_before_refresh():
    assert Zappi(AsyncMock(spec=Connection), 123).serial_number == 123


def test_boost_energy_reads_the_history_producers_key():
    device = Zappi(AsyncMock(spec=Connection), 123)
    device.history_data = {"device_boosted": 2.5}
    assert device.energy_boost == 2.5


def test_vhub_flag_tracks_refreshed_data():
    device = Zappi(AsyncMock(spec=Connection), 123, {"isVHubEnabled": False})
    device.data = {"isVHubEnabled": True}
    assert device.is_vhub_enabled is True
    device.data = {}
    assert device.is_vhub_enabled is False


def test_libbi_without_vhub_contributes_history_totals():
    connection = AsyncMock(spec=Connection)
    device = Libbi(connection, 123, {"sno": 123})
    assert device.kind == LIBBI
    device.history_data = {"generated": 4.5, "grid_import": 1.0, "grid_export": 0.2}
    client = MyenergiClient(connection)
    client.devices = {123: device}
    client._calculate_history_totals()
    assert client.energy_generated == 4.5
    assert client.energy_imported == 1.0
    assert client.energy_exported == 0.2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action,args", [("boost", []), ("smart-boost", []), ("smart-boost", ["2"])]
)
async def test_cli_missing_boost_arguments_fail_before_credentials_or_network(
    action, args
):
    namespace = SimpleNamespace(version=False, command=ZAPPI, action=action, arg=args)
    with pytest.raises(SystemExit):
        await main(namespace)


@pytest.mark.asyncio
async def test_cli_unlock_calls_the_existing_sdk_method(monkeypatch):
    device = AsyncMock(spec=Zappi)
    monkeypatch.setattr(
        "pymyenergi.cli.Connection", lambda *args: AsyncMock(spec=Connection)
    )
    monkeypatch.setattr("pymyenergi.cli.device_factory", lambda *args: device)
    args = SimpleNamespace(
        version=False,
        username="hub",
        password="key",
        skip_oauth=True,
        debug=False,
        command=ZAPPI,
        serial=123,
        action="unlock",
        arg=[],
        json=False,
    )
    await main(args)
    device.unlock.assert_awaited_once_with()
