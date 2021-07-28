import configparser
import texttable
import os
from collections import OrderedDict
from pprint import pprint


class MultiOrderedDict(OrderedDict):

    def __setitem__(self, key, value):

        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)


class Section(configparser.ConfigParser):
    """
    Class for a section of a .conf/.ini file, a section defined as the starting [section] until
    the next [section] beginning and all it's values.
    """
    def __init__(self, filename, key):
        self.key = key

        # Instantiante ConfigParser
        conf = configparser.RawConfigParser(
            dict_type=MultiOrderedDict, strict=False)
        conf.read([filename])

        self.config = conf


class Concentrator(Section):
    """
    Class representing a concentrator from the configuration files 'concentrator= ...', and it's attributes.
    """
    def __init__(self, filename, section):
        super().__init__(filename, section)
        self.read_configuration()

    def read_configuration(self):
        """
        Method which reads the value of the concentrator from the specified section of the configuration file,
        extracting the comma sepaarated values and assigning them to the proper class attribute.
        """
        values = self.config[self.key]['CONCENTRATOR'].split(',')

        self.all_attributes = values
        self.CO_TSAP_ID = values[0]
        self.CO_ID = values[1]
        self.Data_Period = values[2]
        self.Data_Phase = values[3]
        self.Data_StaleLimit = values[4]
        self.Data_version = values[5]
        self.interfaceType = values[6]

    def print_configuration(self):
        """
        Method to print a Concentrator object attributes as ASCII table.
        """
        # Create list to be passed to texttable and to STDOUT
        concentrator_data = self.all_attributes
        concentrator_data.append(self.key)

        # Create texttable
        table = texttable.Texttable()
        table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c"])
        table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m"])
        table.add_rows([["CO_TSAP_ID", "CO_ID", "Data_Period", "Data_Phase", "Data_StaleLimit", "Data_version", "interfaceType", "KEY"],
                        concentrator_data])
        print(table.draw())


class Channel(Section):
    """
    Class representing all channels from the configuration files 'channel= ...', class which will iterate over
    all channels from the specified sections.
    """
    def __init__(self, filename, section):
        super().__init__(filename, section)
        self.read_configuration()

    def read_configuration(self):
        """
        Function which reads the value of the concentrator from the specified section of the configuration file,
        extracting the comma sepaarated values and assigning them to the proper class attribute. Using a for loop
        all the possible channel values will be iterated over from the defined section.
        :return self.channels- a list of dictionaries for each channel:
        """
        self.channels = []

        # Get all rows with 'channel=' and split by newline
        all_channels = self.config.get(self.key, 'CHANNEL')
        channels_data = all_channels.split('\n')

        # Iterate over all channels and create a list of dicts
        for index in range(0, len(channels_data)):

            # Differentiate attributes by comma
            attributes = channels_data[index].split(',')
            
            attributes_dict = {
                "TSAP_ID": attributes[0],
                "ObjID": attributes[1],
                "AttrID": attributes[2],
                "Index1": attributes[3],
                "Index2": attributes[4],
                "format": attributes[5],
                "name": attributes[6],
                "unit": attributes[7],
                "withStatus": attributes[-1]
            }

            self.channels.append(attributes_dict)

    def print_configuration(self):
        """
        Method to print a Channel object attributes as ASCII table.
        """
        # Create list to be passed to texttable and to STDOUT
        channel_data = self.all_attributes
        channel_data.append(self.key)
        channel_data.append(self.channel)

        # Create texttable
        table = texttable.Texttable()
        table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c"])
        table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m"])
        table.add_rows([["TSAP_ID", "ObjID", "AttrID", "Index1", "Index2", "Status", "KEY", "CHANNEL"],
                        channel_data])
        print(table.draw())


class Register(Section):
    """
    Class representing all register values from the configuration files 'register= ...', class which will iterate over
    all the types registers from the specified file.
    """
    def __init__(self, filename, section="INPUT_REGISTERS"):
        super().__init__(filename, section)
        self.read_configuration()

    def read_configuration(self):
        """
        Function which reads the value of the register from the specified section of the configuration file,
        extracting the comma separated values and assigning them to the proper class attribute. Using a for loop
        all the possible register values will be iterated over from the defined section.
        :return self.channels- a list of dictionaries for each register:
        """

        # Grab all 'registers=' and separate them based on newline
        all_registers = self.config.get(self.key, 'REGISTER')
        registers_data = all_registers.split('\n')

        self.registers = []

        # Iterate over available registers
        for index in range(0, len(registers_data)):

            # Differentiate attributes by comma
            attributes = registers_data[index].split(',')
            
            registers_dict = {
                'start_addr': attributes[0],
                'word_cnt': attributes[1],
                'EUI64': attributes[2],
                'TSAPID': attributes[3],
                'ObjId': attributes[4],
                'AttrId': attributes[5],
                'Idx1': attributes[6],
                'Idx2': attributes[7],
                'MethId': attributes[8],
                'status': attributes[-1]
            }

            self.registers.append(registers_dict)


class Context():
    """
    Class to read the configuration file for the application to create an object
    used for passing in between py modules for utilising those values in certain functions
    """
    def __init__(self):
        self.read_context()

    def read_context(self):
        # Read configuration file for application and set attributes
        conf = configparser.RawConfigParser(strict=False)
        conf.read(['context.ini'])

        self.in_gw = conf['working_context']['in_gw']
        self.in_hosts = conf['working_context']['in_hosts']
        self.interval = conf['working_context']['interval']
        self.out_gateway = conf['working_context']['out_gw']
        self.out_hosts = conf['working_context']['out_hosts']
        self.output_file = conf['working_context']['resp_file']
        self.address = conf['working_context']['address']
        self.port = conf['working_context']['port']

# Instantiate Context object
settings = Context()