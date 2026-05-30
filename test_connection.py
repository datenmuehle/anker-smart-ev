import asyncio
import sys
from pymodbus.client import AsyncModbusTcpClient

# Robust Endian import
try:
    from pymodbus.constants import Endian
except ImportError:
    try:
        from pymodbus.framer import Endian
    except ImportError:
        class Endian:
            BIG = "big"

async def test_charger(host, port=502):
    print(f"--- Anker SOLIX V1 Diagnostic Tool ---")
    print(f"Connecting to {host}:{port}...")
    
    client = AsyncModbusTcpClient(host, port=port)
    
    if not await client.connect():
        print("Error: Could not connect to the charger. Check IP and Modbus TCP settings in the App.")
        return

    print("Connected successfully!\n")

    def decode_string(registers):
        s = ""
        for reg in registers:
            s += chr(reg >> 8) + chr(reg & 0xFF)
        return s.strip("\x00")

    def decode_uint32(registers):
        return client.convert_from_registers(
            registers,
            data_type=client.DATATYPE.UINT32,
            word_order=Endian.BIG
        )

    try:
        # 1. Read Intrinsic Information
        # Model Name: 20001 (10 regs)
        # Serial Number: 20011 (12 regs)
        res_info = await client.read_holding_registers(20001, count=22, device_id=1)
        if not res_info.isError():
            model = decode_string(res_info.registers[0:10])
            serial = decode_string(res_info.registers[10:22])
            print(f"Model Name:    {model}")
            print(f"Serial Number: {serial}")
        else:
            print("Could not read identification registers.")

        # 2. Read Live Data
        # L1 Voltage: 20053 (1 reg, Gain 10)
        # L1 Current: 20059 (1 reg, Gain 100)
        # Total Power: 20068 (2 regs, UINT32)
        # Status: 20097 (1 reg)
        res_live = await client.read_holding_registers(20053, count=45, device_id=1)
        if not res_live.isError():
            regs = res_live.registers
            voltage = regs[0] / 10.0
            current = regs[6] / 100.0
            power = decode_uint32(regs[15:17])
            status_code = regs[44]
            
            status_map = {0:"Idle", 1:"Preparing", 2:"Charging", 3:"Paused", 5:"Completed", 8:"Error"}
            status_text = status_map.get(status_code, f"Unknown ({status_code})")

            print(f"L1 Voltage:    {voltage} V")
            print(f"L1 Current:    {current} A")
            print(f"Total Power:   {power} W")
            print(f"Status:        {status_text}")
        else:
            print("Could not read live data registers.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        client.close()
        print("\nDisconnected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <CHARGER_IP>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    asyncio.run(test_charger(target_ip))
