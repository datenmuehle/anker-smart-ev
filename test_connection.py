import asyncio
import sys
import traceback
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
    
    try:
        connected = await client.connect()
        if not connected:
            print(f"FAILED: Could not connect to {host}:{port}.")
            print("Troubleshooting: Check IP address, ensure phone app has Modbus TCP enabled, and verify no other device is already connected (max 2 clients).")
            return
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        traceback.print_exc()
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
        print("Reading identification registers [20001-20022]...")
        res_info = await client.read_holding_registers(20001, count=22, device_id=1)
        if not res_info.isError():
            model = decode_string(res_info.registers[0:10])
            serial = decode_string(res_info.registers[10:22])
            print(f"  Model Name:    {model}")
            print(f"  Serial Number: {serial}")
        else:
            print(f"  READ ERROR (Info): {res_info}")
            if hasattr(res_info, 'message'):
                print(f"  Message: {res_info.message}")

        print("\nReading live data registers [20053-20097]...")
        # 2. Read Live Data
        res_live = await client.read_holding_registers(20053, count=45, device_id=1)
        if not res_live.isError():
            regs = res_live.registers
            voltage = regs[0] / 10.0
            current = regs[6] / 100.0
            power = decode_uint32(regs[15:17])
            status_code = regs[44]
            
            status_map = {0:"Idle", 1:"Preparing", 2:"Charging", 3:"Paused", 5:"Completed", 8:"Error"}
            status_text = status_map.get(status_code, f"Unknown ({status_code})")

            print(f"  L1 Voltage:    {voltage} V")
            print(f"  L1 Current:    {current} A")
            print(f"  Total Power:   {power} W")
            print(f"  Status:        {status_text}")
        else:
            print(f"  READ ERROR (Live): {res_live}")

    except Exception as e:
        print(f"\nUNEXPECTED ERROR DURING DATA FETCH: {e}")
        traceback.print_exc()
    finally:
        client.close()
        print("\nDisconnected.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <CHARGER_IP>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    asyncio.run(test_charger(target_ip))
