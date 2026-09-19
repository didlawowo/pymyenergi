from unittest.mock import AsyncMock

import pytest

from pymyenergi.zappi import Zappi

pytestmark = pytest.mark.asyncio


async def test_refresh(zappi_fetch_data_fixture, zappi_fetch_boost_data_fixture):
    """Test Zappi data"""
    zappi = Zappi({}, 16042300)
    await zappi.refresh()
    assert zappi.serial_number == 16042300
    assert zappi.charge_mode == "Fast"
    assert zappi.charge_added == 4.2


async def test_set_phase_setting_updates_local_state():
    connection = AsyncMock()
    zappi = Zappi(connection, 16042300, {"phaseSetting": "SINGLE_PHASE"})

    await zappi.set_phase_setting("3")

    connection.get.assert_awaited_once_with("/cgi-zappi-phase-setting-Z16042300-1")
    assert zappi.num_phases == "3"
