from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ADDR_PHASE_SETTING

PHASE_MODES = {
    0: "Automatic",
    1: "Fixed Single-Phase",
    2: "Fixed Three-Phase",
}
PHASE_MODES_INV = {v: k for k, v in PHASE_MODES.items()}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnkerSolixPhaseSelect(coordinator)])

class AnkerSolixPhaseSelect(CoordinatorEntity, SelectEntity):
    """Phase mode selection."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Anker SOLIX Phase Mode"
        self._attr_unique_id = f"{coordinator.hub._host}_phase_mode"
        self._attr_options = list(PHASE_MODES.values())

    @property
    def current_option(self):
        """Return the current option."""
        mode = self.coordinator.data.get("phase_mode")
        return PHASE_MODES.get(mode)

    async def async_select_option(self, option: str):
        """Change the phase mode."""
        mode = PHASE_MODES_INV.get(option)
        if mode is not None:
            if await self.coordinator.hub.write_register(ADDR_PHASE_SETTING, mode):
                await self.coordinator.async_request_refresh()
