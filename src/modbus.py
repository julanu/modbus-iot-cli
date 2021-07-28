from pymodbus.client.sync import ModbusTcpClient
from classes import settings
from time import gmtime, strftime
import os
import json


def create_conn(address='127.0.0.1', port='502'):
    """
    Function to create a TCP/IP connection to a MODBUS slave to localhost on port 502 if no address/port is specified.
    :param address - IP address of network:
    :param port - port for TCP/IP connection:
    :return client - connection to the MODBUS slave:
    """

    client = ModbusTcpClient(address, port=port)
    client.connect()

    return client


def disconnect(conn):
    """
    Method to close our TCP/IP connection to the MODBUS client.
    :param conn - connection to MODBUS client:
    :return resp - response from close() method:
    """
    resp = None

    try:
        conn.close()
        resp = 200
    except Exception as e:
        print(f"Caught exception when trying to close connection:\n {e}")
        resp = 400
    
    return resp


def read_input_reg(conn, filename_gw):
    """
    """

    # Read the mapped gateway configuration
    with open(settings.out_gateway, "r") as f_gw:
        data = json.load(f_gw)

    trans_id = 0  # transaction id when reading registers
    json_data = {}

    for mapping in data["INPUT_REGISTERS"]["registers"]:

        # get the register addr and how many regs to read
        start_addr = int(mapping.get("start_addr", None))
        word_count = int(mapping.get("word_cnt", None))

        # device ID
        eui64 = mapping.get("EUI64", None)

        # read from the registers and record the moment in time
        reg = conn.read_input_registers(start_addr, word_count)
        datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        x = reg.registers
        
        # create a response and save the data
        r = {
            "register": start_addr,
             "response": x,
             "device": eui64,
             "last_read": datetime
            }

        json_data[trans_id] = r

        trans_id += 1

    # write data in response file
    with open(settings.output_file, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    return json_data
