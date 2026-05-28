"""Constants for the Anker SOLIX V1 Smart EV Charger integration."""

DOMAIN = "anker_solix_ev"
DEFAULT_NAME = "Anker SOLIX EV Charger"
DEFAULT_PORT = 502
SCAN_INTERVAL = 30

# Register Addresses
ADDR_PRODUCT_NUMBER = 20000
ADDR_MODEL_NAME = 20001
ADDR_SERIAL_NUMBER = 20011
ADDR_SOFTWARE_VERSION = 20023
ADDR_HARDWARE_VERSION = 20029

ADDR_L1_N_VOLTAGE = 20053
ADDR_L2_N_VOLTAGE = 20054
ADDR_L3_N_VOLTAGE = 20055

ADDR_L1_CURRENT = 20059
ADDR_L2_CURRENT = 20060
ADDR_L3_CURRENT = 20061

ADDR_TOTAL_ACTIVE_POWER = 20068  # UINT32 (2 registers)

ADDR_SESSION_DURATION = 20082    # UINT32 (2 registers)
ADDR_SESSION_CAPACITY = 20084    # UINT32 (2 registers)

ADDR_CHARGING_STATUS = 20097

# Control Registers
ADDR_CHARGING_COMMAND = 21000
ADDR_MAX_CURRENT_SETTING = 21001
ADDR_PHASE_SETTING = 21005

# Gains
GAIN_VOLTAGE = 10.0
GAIN_CURRENT = 100.0
GAIN_CURRENT_LIMIT = 10.0 # From OCR: "W" unit but context implies Amps with Gain 10

# Status Mapping
CHARGING_STATUS_MAP = {
    0: "Idle",
    1: "Preparing",
    2: "Charging",
    3: "Charger Paused",
    4: "Vehicle Paused",
    5: "Charging Completed",
    6: "Reserving",
    7: "Disabled",
    8: "Error",
}
