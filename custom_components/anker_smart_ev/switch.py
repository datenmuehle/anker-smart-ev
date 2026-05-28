from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ADDR_CHARGING_COMMAND

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnkerSolixSwitch(coordinator)])

class AnkerSolixSwitch(CoordinatorEntity, SwitchEntity):
    """Charging control switch."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Anker SOLIX Charging"
        self._attr_unique_id = f"{coordinator.hub._host}_charging"
        self._attr_device_class = SwitchDeviceClass.OUTLET

    @property
    def is_on(self):
        """Return true if charging."""
        return self.coordinator.data.get("status") == 2

    async def async_turn_on(self, **kwargs):
        """Start charging."""
        if await self.coordinator.hub.write_register(ADDR_CHARGING_COMMAND, 1):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Stop charging."""
        if await self.coordinator.hub.write_register(ADDR_CHARGING_COMMAND, 2):
            await self.coordinator.async_request_refresh()
