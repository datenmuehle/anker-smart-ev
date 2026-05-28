import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient

# Robust Endian import for different pymodbus 3.x versions
try:
    from pymodbus.constants import Endian
except ImportError:
    try:
        from pymodbus.framer import Endian
    except ImportError:
        # Fallback for very specific 3.x sub-versions
        class Endian:
            BIG = "big"
            LITTLE = "little"

_LOGGER = logging.getLogger(__name__)

class AnkerSolixHub:
    """Modbus hub for Anker SOLIX EV Charger."""

    def __init__(self, host, port=502):
        self._host = host
        self._port = port
        self._client = AsyncModbusTcpClient(host, port=port)
        self._lock = asyncio.Lock()

    async def connect(self):
        """Connect to the charger."""
        if not self._client.connected:
            return await self._client.connect()
        return True

    def disconnect(self):
        """Disconnect from the charger."""
        self._client.close()

    async def read_registers(self, address, count):
        """Read holding registers."""
        async with self._lock:
            if not await self.connect():
                return None
            try:
                result = await self._client.read_holding_registers(address, count, slave=1)
                if result.isError():
                    _LOGGER.error("Modbus error reading address %s: %s", address, result)
                    return None
                return result.registers
            except Exception as e:
                _LOGGER.error("Exception reading Modbus address %s: %s", address, e)
                return None

    async def write_register(self, address, value):
        """Write holding register."""
        async with self._lock:
            if not await self.connect():
                return False
            try:
                result = await self._client.write_register(address, value, slave=1)
                return not result.isError()
            except Exception as e:
                _LOGGER.error("Exception writing Modbus address %s: %s", address, e)
                return False

    def decode_uint32(self, registers):
        """Decode two 16-bit registers into a uint32 (pymodbus 3.11+)."""
        # pymodbus 3.11+ helper only takes word_order, byte_order is assumed Big
        return self._client.convert_from_registers(
            registers,
            data_type=self._client.DATATYPE.UINT32,
            word_order=Endian.BIG
        )

    def decode_string(self, registers):
        """Decode registers into a string (Manual decode for BIG endian)."""
        s = ""
        for reg in registers:
            s += chr(reg >> 8) + chr(reg & 0xFF)
        return s.strip("\x00")
