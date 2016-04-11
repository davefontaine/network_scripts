#!/usr/bin/python
#
# create_dns_record.py
#   input: list of filenames to parse; filename must contain hostname eg. lca1-crt01.nw-config.txt
#   output: a dns entry to stdout for 
# 

import sys
import re
from ciscoconfparse import CiscoConfParse

# site code
all_sites = ["lca1", "lva1"]

# enviornment code
all_environments = ["nw", "corp", "prod"]

# mapping of cli interface name string to abbreviated DNS string
interface_name_mapping = {
    'Loopback':'lo',
    'Ethernet':'eth',
    'GigabitEthernet':'ge',
    'TenGigabitEthernet':'te',
    'Vlan':'vlan',
    'xe':'xe'
}

# remove executable file name from list, leaves list of files
sys.argv.remove(sys.argv[0])

hostname_re = re.compile(r'.*((' + "|".join(all_sites) + r')(.*)\.(' + "|".join(all_environments) + r')).*')
ipv6_address_re = re.compile(r".*ipv6 address\W(.*)/[0-9]+")
interface_re = re.compile(r"^interface ([a-zA-Z]+)([0-9]+)/?([0-9]+)?/?([0-9]+)?")
junos_ipv6_interface_re = re.compile(r'^set interfaces (.*) unit \d+ family inet6 address (.*)/[0-9]+')

# incomplete items
# if match is Loopback interface, create DNS entry for device 

def write_dns_record_stdout(hostname_str, interface_string, ipv6_address_string):
    if interface_string.find("lo") < 0:
        print hostname_str + '-' + interface_string + '.' + environment + '.' + 'linkedin.com' + ' AAAA ' + ipv6_address
    else:
        print hostname_str + '.' + environment + '.' + 'linkedin.com' + ' AAAA ' + ipv6_address


for file in sys.argv:

    m = hostname_re.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2)+m.group(3)
        environment = m.group(4)

    # otherwise, do not process / parse the file
    else:
        print 'Filename "' + file + '" does not contain device hostname.'
        continue

    # parse the file
    parsed_file = CiscoConfParse(file)

    # pull out all interfaces which have an ipv6 address
    interfaces = parsed_file.find_objects_w_child(parentspec=r"^interface", childspec=r"ipv6 address")

    # if the list is not empty this is likely a Cisco-like device
    if interfaces != []:
        # for every interface that matches the above conditions, 
        for interface_name in interfaces:
            match_interface_name = interface_re.match(interface_name.text)
            short_interface_name = interface_name_mapping[match_interface_name.group(1)]
            
            # build interface port number with "/" substituded by "-"
            #  eg. Ethernet1/2 becomes eth1-2
            #  do this for all except loopback interface which becomes host entry
            if match_interface_name.lastindex >= 2:
                short_interface_name += '-' + match_interface_name.group(2)
            if match_interface_name.lastindex >= 3:
                short_interface_name += '-' + match_interface_name.group(3)
            if match_interface_name.lastindex >= 4:
                short_interface_name += '-' + match_interface_name.group(4)

            # find "ipv6 address" under interface and grab address
            for subinterface_line in interface_name.children:
                match_ipv6_address = ipv6_address_re.match(subinterface_line.text)
                if match_ipv6_address:
                    ipv6_address = match_ipv6_address.group(1)

            # create record by merging dns_name and ipv6 address and write entry to stdout
            write_dns_record_stdout(hostname, short_interface_name, ipv6_address)
    # here we assume it's JUNOS, since the cisco parser came back NULL
    else:
        with open(file) as f:
            entire_config = f.readlines()
        for line in entire_config:
            match_interface_name = junos_ipv6_interface_re.match(line)
            if match_interface_name:
                interface_name = match_interface_name.group(1)
                ipv6_address = match_interface_name.group(2)
                interface_name.replace("/", "-")
                write_dns_record_stdout(hostname, interface_name, ipv6_address)
    continue


































