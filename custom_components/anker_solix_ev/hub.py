import asyncio
import logging
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

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
        """Decode two 16-bit registers into a uint32."""
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        return decoder.decode_32bit_uint()

    def decode_string(self, registers):
        """Decode registers into a string."""
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        return decoder.decode_string(len(registers) * 2).decode("ascii").strip("\x00")
