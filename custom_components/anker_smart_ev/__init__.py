import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_HOST, CONF_PORT, Platform

from .const import (
    DOMAIN, SCAN_INTERVAL, 
    ADDR_L1_N_VOLTAGE, ADDR_L2_N_VOLTAGE, ADDR_L3_N_VOLTAGE,
    ADDR_L1_CURRENT, ADDR_L2_CURRENT, ADDR_L3_CURRENT,
    ADDR_TOTAL_ACTIVE_POWER, ADDR_SESSION_DURATION, ADDR_SESSION_CAPACITY,
    ADDR_CHARGING_STATUS, ADDR_CHARGING_COMMAND, ADDR_MAX_CURRENT_SETTING, ADDR_PHASE_SETTING
)
from .hub import AnkerSolixHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anker SOLIX EV Charger from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 502)
    hub = AnkerSolixHub(host, port)

    coordinator = AnkerSolixCoordinator(hass, hub)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.hub.disconnect()
    return unload_ok

class AnkerSolixCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching data from the charger."""

    def __init__(self, hass, hub):
        """Initialize the coordinator."""
        self.hub = hub
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from Modbus."""
        data = {}
        # Bulk read monitoring registers (20053 to 20100 approx)
        # We'll read in smaller blocks for reliability if needed, 
        # but 20053 to 20097 is ~45 registers.
        regs = await self.hub.read_registers(ADDR_L1_N_VOLTAGE, 45)
        if regs:
            # Map registers (relative to ADDR_L1_N_VOLTAGE = 20053)
            data["voltage_l1"] = regs[0]
            data["voltage_l2"] = regs[1]
            data["voltage_l3"] = regs[2]
            data["current_l1"] = regs[6]
            data["current_l2"] = regs[7]
            data["current_l3"] = regs[8]
            
            # Active Power (UINT32)
            data["power_l1"] = self.hub.decode_uint32(regs[9:11])
            data["power_l2"] = self.hub.decode_uint32(regs[11:13])
            data["power_l3"] = self.hub.decode_uint32(regs[13:15])
            
            # Power (UINT32 at offset 15: 20068)
            data["total_power"] = self.hub.decode_uint32(regs[15:17])
            
            # Duration (UINT32 at offset 29: 20082)
            data["session_duration"] = self.hub.decode_uint32(regs[29:31])
            # Capacity (UINT32 at offset 31: 20084)
            data["session_capacity"] = self.hub.decode_uint32(regs[31:33])
            
            # Status (UINT16 at offset 44: 20097)
            data["status"] = regs[44]

        # Read control registers (21000 range)
        ctrl_regs = await self.hub.read_registers(ADDR_CHARGING_COMMAND, 6)
        if ctrl_regs:
            data["max_current"] = ctrl_regs[1]
            data["phase_mode"] = ctrl_regs[5]

        if not data:
            raise UpdateFailed("Error fetching data from Modbus")

        return data
