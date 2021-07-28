import configparser
from classes import Concentrator, Register, Section, MultiOrderedDict, Channel, settings
import texttable
import random
import json

# Statuses used for data availability
status = ["Fresh", "Stale"]


def map_host_publishers(filename):
    """
    Function to map the publishers configuration file and output all data in a JSON file
    :param filename - file to be parsed and mapped:
    :return - path to output file:
    """
    config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)
    config.read(filename)

    json_data = {}

    for section in config.sections():
        json_section = {}

        # Create read objects as dictionaries
        concentrator_obj = Concentrator(filename, section).__dict__
        channel_obj = Channel(filename, section).__dict__

        # Remove unecessary keys
        concentrator_obj.pop('config', None)
        concentrator_obj.pop('key', None)
        channel_obj.pop('config', None)

        # Create concentrator section
        json_section['concentrator'] = concentrator_obj

        # Remove colon from section name
        section = ''.join(section.split(':'))

        json_section[section] = channel_obj
        json_data[section] = json_section

    # Write mapped data to a JSON file
    with open(settings.out_hosts, 'w+') as json_file:
        json.dump(json_data, json_file, indent=4, sort_keys=True)

    return settings.out_hosts


def map_modbus_gw(filename):
    """
    Function to map the specified MODBUS gateway file, and create in response a JSON file
    with all register values and attributes
    :param filename - path to gateway file:
    :return - path to output file:
    """
    config = configparser.RawConfigParser(dict_type=MultiOrderedDict, strict=False)
    config.read(filename)

    json_data = {}

    for section in config.sections():
        
        # Create dict from object
        register_obj = Register(filename, section).__dict__

        section_key = register_obj.get('key', 'DEFAULT')

        # Remove uncessary attributes
        register_obj.pop('config', None)
        register_obj.pop('key', None)

        json_data[section_key] = register_obj

    # Write mapped data to a JSON file
    with open(settings.out_gateway, 'w+') as json_file:
        json.dump(json_data, json_file, indent=4, sort_keys=True)

    return settings.out_gateway


def print_all_sections(filename):
    """
    Method which will print all the sections from a specified configuration file.
    :param filename - configuration file:
    :return:
    """
    # Create table
    table = texttable.Texttable()

    # Initiate file parser
    conf = configparser.RawConfigParser(
        dict_type=MultiOrderedDict, strict=False)
    conf.read([filename])

    # Print all sections available in the file
    available_sections = [[]]
    for each_section in conf.sections():
        available_sections.append([each_section])

    table.add_rows(available_sections)
    table.set_cols_align(["c"])
    table.set_cols_valign(["m"])
    table.header([f"Sections {filename.split('/')[-1]}"])

    print(table.draw())


def print_gw_table(filename):
    """
    Method to display as an ASCII table the MODBUS gateway configuration file specified.
    """

    with open(filename, "r") as f:
        data = json.load(f)

    # Create texttable
    table = texttable.Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m", "m", "m"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m", "m", "m"])

    for mapping in data["INPUT_REGISTERS"]["registers"]:

        register_attributes = list(mapping.values())

        table.add_rows([["AttrId", "EUI64", "Idx1", "Idx2", "MethId", "ObjId", "TSAPID", "start_addr", "status", "word_cnt"],
                        register_attributes])

    print(table.draw())


def print_hosts_table(filename_hosts, filename_gw):
    """
    Method to display as an ASCII table the HOSTS PUBLISHERS specified file data based on the MODBUS 
    gateway configuration file specified too.
    """

    # Load mapped configuration for gateway and .conf file
    with open(filename_gw, "r") as f:
        gw_data = json.load(f)

    with open(filename_hosts, "r") as f2:
        hosts_data = json.load(f2)

    # Create texttable
    table = texttable.Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m"])
    table.set_cols_dtype(['t', 'i', 'i', 'i', 'i', 'i', 'i', 't', 't', 't', 'i'])

    # Iterate over mapped gateway data
    for reg in gw_data["INPUT_REGISTERS"]["registers"]:
        
        # Get device ID and count mapped channels
        eui64 = reg.get('EUI64', None)
        ch_number = 1

        # Iterate over channels of each device
        for ch in hosts_data[eui64][eui64]['channels']:

            # Grab channel attributes and start creating list for table
            ch = list(ch.values())

            ch.insert(0, eui64) 
            ch.insert(1, ch_number)

            ch_number += 1

            table.add_rows([["EUI64", "Channel no.", "AttrID", "Index1", "Index2", "ObjId", "TSAPID",
                             "Format", "Name", "Unit", "withStatus"], ch])

    print(table.draw())


def interpret_response_data(filename_resp):
    """
    Function to load the mapped JSON files(the configuration data) which suggest how we can interpret the result
    when reading data from the MODBUS slave.
    :param :
    :return :
    """

    # Load all JSON files with mapped data
    with open(filename_resp, "r") as f:
        resp = json.load(f)

    with open(settings.out_hosts, "r") as f_hosts:
        hosts_data = json.load(f_hosts)

    with open(settings.out_gateway, "r") as f_gw:
        gw_data = json.load(f_gw)

     # Create texttable
    table = texttable.Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m"])
    table.set_cols_dtype(['t', 'i', 'i', 'i', 'i'])

    # Iterate over a dict of dicts
    for majorkey, subdict in resp.items():
        data_list = []
        
        # Get device ID and last time the values were read
        device = subdict['device']
        last_read = subdict['last_read']
        index = 0
        
        # Iterate over mapped channels of each device
        for ch in hosts_data[device][device]['channels']:
            
            # Start creating the necessary lists to output as ASCII table
            if index < len(subdict['response']):
                data_list = []

                data_list.append(device)

                measurement_unit = ch.get('unit', None)   
                sensor_value = subdict['response'][index]
                
                data_list.append(sensor_value)
                data_list.append(measurement_unit)
                data_list.append(last_read)

                curr_status = random.choice(status)
                data_list.append(curr_status) # status

                index += 1

                table.add_rows([["Device", "Value", "Unit of Measurement", "Last Read", "Status"],
                                data_list])

    print(table.draw())
