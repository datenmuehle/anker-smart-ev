from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ADDR_MAX_CURRENT_SETTING, GAIN_CURRENT_LIMIT

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnkerSolixCurrentLimit(coordinator)])

class AnkerSolixCurrentLimit(CoordinatorEntity, NumberEntity):
    """Current limit setting."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Anker SOLIX Max Current"
        self._attr_unique_id = f"{coordinator.hub._host}_max_current"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = NumberDeviceClass.CURRENT
        self._attr_native_min_value = 6.0
        self._attr_native_max_value = 32.0
        self._attr_native_step = 1.0

    @property
    def native_value(self):
        """Return the current limit."""
        val = self.coordinator.data.get("max_current")
        if val is None:
            return None
        return val / GAIN_CURRENT_LIMIT

    async def async_set_native_value(self, value: float):
        """Update the current limit."""
        raw_value = int(value * GAIN_CURRENT_LIMIT)
        if await self.coordinator.hub.write_register(ADDR_MAX_CURRENT_SETTING, raw_value):
            await self.coordinator.async_request_refresh()
