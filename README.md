# README #

IOT Project, CLI Application

### TODO 
* Add terminal colors
* Refactor argparser
* Add project setup and usage

### Available cmds ###
```
--version  display current version of app
--help     displays all available cli cmds 

## Functionality done 
--display_sections, -ds [file]
    display all sections from the configuration file

## Display help
python .\arg_parser.py --help

## Display modbus gateway
python .\arg_parser.py --display_gateway_conf ../conf/modbus_gw.ini 

## Display host publishers data
python .\arg_parser.py --display_hosts_pub ../conf/host_publishers.conf ../conf/modbus_gw.ini  

## Read all registers based on conf files
python arg_parser.py --read_all_registers True

## Interpret data
python .\arg_parser.py --interpret_data ../out/response.json


# To implement:
--verbose, -v [value]
    set logging level to [value]

--set_context [gateway, hosts]
    sets at the application level that the two working files will be <gateway> and <hosts>

--get-context 
    display the current files from which the application fetches data
------------------------------------------


### What is this repository for? ###

* CLI Application to fetch data using MODBUS

### How do I get set up? ###

* Configuration
* Dependencies
