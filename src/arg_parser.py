import json
import time
import os.path
import argparse
import texttable
import configparser
from multiprocessing import Process

import modbus
from file_parser import *
from pymodbus.client.sync import ModbusTcpClient
from classes import Concentrator, Register, Section, MultiOrderedDict, Channel, settings

parser = argparse.ArgumentParser(prog='arg_parser.py',
        description='List the available commands when working with a MODBUS configuration.')

parser.add_argument('--verbose', '-v',
                    dest='level',
                    help='Increase output verbosity by specifying the level.',
                    type=bool,
                    nargs='+')

parser.add_argument('--display_gateway_conf', '-dgw',
                    dest='gateway_conf_file',
                    help='Display as ASCII table the values under the specified MODBUS gateway config file',
                    type=str,
                    nargs='+')

parser.add_argument('--display_hosts_pub', '-dhp',
                    dest='conf_file',
                    help='Display as ASCII table the values under the specified MODBUS gateway and hosts publishers config file',
                    type=str,
                    nargs='+')

parser.add_argument('--disp_channel', '-dch',
                    dest='hosts_conf_file',
                    help='Display as ASCII table all channels from specified file',
                    type=str,
                    nargs='+')

parser.add_argument('--disp_concentrator', '-dcon',
                    dest='hosts_conf_file',
                    help='Display as ASCII table all concentrators from specified file',
                    type=str,
                    nargs='+')

parser.add_argument('--disp_register', '-dr',
                    dest='gateway_conf_file',
                    help='Display as ASCII all register values from specified gateway file',
                    type=str,
                    nargs='+')

parser.add_argument('--read_all_registers',
                    dest='bool_value',
                    help='Based on the input configuration files, read all registers specified and save the \
                          reponse as JSON format for interpretation.',
                    type=str,
                    nargs='+')

parser.add_argument('--interpret_data',
                    dest='output_file',
                    help='Display information about latest read data from the response file',
                    type=str,
                    nargs='+')

parser.add_argument('--display_sections',
                    dest='conf_file',
                    help='Display all sections from the specified file.',
                    type=str,
                    nargs='+')

args = parser.parse_args()


def synchronize_data():
    """
    Method to run at a set interval of seconds to refresh the data from the MODBUS server.
    """
    try:
        exec_index = 0
        while(True):
            print(f"Executing refresh #{exec_index} for data synchronization")
            map_modbus_gw(settings.in_gw)
            map_host_publishers(settings.in_hosts)
            
            os.system('cls')

            client = modbus.create_conn(settings.address, settings.port)
            modbus.read_input_reg(client, settings.out_gateway)
            resp = modbus.disconnect(client)

            interpret_response_data(settings.output_file)

            time.sleep(int(settings.interval))
            exec_index += 1

    except Exception as e:
        print(f"Encountered error when syncing files: {e}")


def main():

    # TODO add comments and refactor interpret data
    # TODO try and color terminal output
    # TODO add clearing of terminal before running certain commands

    address = "127.0.0.1"
    port = 502

    if args.level:
        print(f"Enable verbose mode: {args.verbose}")

    # SECTIONS of a file
    if args.conf_file and os.path.exists(args.conf_file[0]):
        print_all_sections(args.conf_file[0])

    # GATEWAY config
    if args.gateway_conf_file and os.path.exists(args.gateway_conf_file[0]):
        gateway = args.gateway_conf_file[0]
        out_gw = map_modbus_gw(gateway)
        print_gw_table(out_gw)

    # HOSTS config
    if args.conf_file and os.path.exists(args.conf_file[0]):

        gateway = args.conf_file[1]
        out_gw = map_modbus_gw(gateway)

        hosts = args.conf_file[0]
        out_host = map_host_publishers(hosts)

        print_hosts_table(out_host, out_gw)

    # INTERPRET data
    if args.output_file:
        interpret_response_data(args.output_file[0])

    if args.bool_value:
        client = modbus.create_conn(address, port)
        modbus.read_input_reg(client, settings.out_gateway)
        resp = modbus.disconnect(client)
        print(f"Response when closing MOBBUS connection: {resp}")


if __name__ == '__main__':
    p1 = Process(target=synchronize_data)
    p1.start()

    p2 = Process(target=main)
    p2.start()

    p1.join()
    p2.join()
