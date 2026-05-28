from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTime,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, GAIN_VOLTAGE, GAIN_CURRENT, CHARGING_STATUS_MAP

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AnkerSolixSensor(coordinator, "Voltage L1", "voltage_l1", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, GAIN_VOLTAGE),
        AnkerSolixSensor(coordinator, "Voltage L2", "voltage_l2", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, GAIN_VOLTAGE),
        AnkerSolixSensor(coordinator, "Voltage L3", "voltage_l3", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, GAIN_VOLTAGE),
        AnkerSolixSensor(coordinator, "Current L1", "current_l1", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, GAIN_CURRENT),
        AnkerSolixSensor(coordinator, "Current L2", "current_l2", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, GAIN_CURRENT),
        AnkerSolixSensor(coordinator, "Current L3", "current_l3", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, GAIN_CURRENT),
        AnkerSolixSensor(coordinator, "Total Power", "total_power", UnitOfPower.WATT, SensorDeviceClass.POWER),
        AnkerSolixSensor(coordinator, "Session Capacity", "session_capacity", UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY, 1.0, SensorStateClass.TOTAL_INCREASING),
        AnkerSolixSensor(coordinator, "Session Duration", "session_duration", UnitOfTime.SECONDS, SensorDeviceClass.DURATION),
        AnkerSolixStatusSensor(coordinator),
    ]
    
    async_add_entities(entities)

class AnkerSolixSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Anker SOLIX EV."""

    def __init__(self, coordinator, name, key, unit=None, device_class=None, gain=1.0, state_class=SensorStateClass.MEASUREMENT):
        super().__init__(coordinator)
        self._attr_name = f"Anker SOLIX {name}"
        self._attr_unique_id = f"{coordinator.hub._host}_{key}"
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._gain = gain

    @property
    def native_value(self):
        """Return the value from the coordinator."""
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        return val / self._gain

class AnkerSolixStatusSensor(CoordinatorEntity, SensorEntity):
    """Status sensor for Anker SOLIX EV."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Anker SOLIX Status"
        self._attr_unique_id = f"{coordinator.hub._host}_status"

    @property
    def native_value(self):
        """Return the status string."""
        status_code = self.coordinator.data.get("status")
        return CHARGING_STATUS_MAP.get(status_code, f"Unknown ({status_code})")
