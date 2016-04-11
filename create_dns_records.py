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

def write_dns_record(hostname_str, interface_string, ipv6_address_string):
    print hostname_str   


for file in sys.argv:

    m = hostname_re.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2)+m.group(3)
        environment= m.group(4)

    # otherwise, do not process / parse the file
    else:
        print 'Filename "' + file + '" does not contain device hostname.'
        continue

    # parse the file
    parsed_file = CiscoConfParse(file)

    # pull out all interfaces which have an ipv6 address
    interfaces = parsed_file.find_objects_w_child(parentspec=r"^interface", childspec=r"ipv6 address")
    #print "DEBUG: Interface list:", interfaces

    # if the list is not empty this is likely a Cisco device
    if interfaces != []:
        #print "DEBUG: This seems to be a Cisco device."
        # for every interface that matches the above conditions, 
        #  - process the interface name 
        #  - convert it to DNS-style string
        #  - print DNS entry
        for interface_name in interfaces:
            match_interface_name = interface_re.match(interface_name.text)
            short_interface_name = interface_name_mapping[match_interface_name.group(1)]
            
            # build interface port number with "/" substituded by "-"
            #  eg. Ethernet1/2 becomes eth1-2
            #  do this for all except loopback interface which becomes host entry
            if short_interface_name != "lo":
                dns_name = hostname + "-" + short_interface_name
                if match_interface_name.lastindex >= 2:
                    dns_name += '-' + match_interface_name.group(2)
                if match_interface_name.lastindex >= 3:
                    dns_name += "-" + match_interface_name.group(3)
                if match_interface_name.lastindex >= 4:
                    dns_name += "-" + match_interface_name.group(4)

            # if loopback interface, generate dns host entry for device, don't include interface string
            else:
                dns_name = hostname

            # find "ipv6 address" under interface and grab address
            for subinterface_line in interface_name.children:
                match_ipv6_address = ipv6_address_re.match(subinterface_line.text)
                if match_ipv6_address:
                    ipv6_address = match_ipv6_address.group(1)

            # create record by merging dns_name and ipv6 address and write entry to stdout
            #write_dns_record_stdout(hostname, 
            dns_name += '.' + environment + '.' + 'linkedin.com'
            dns_record = dns_name + ' AAAA ' + ipv6_address
            print dns_record
    else:
        #print "DEBUG: This may be a JUNOS device."
        with open(file) as f:
            entire_config = f.readlines()
        for line in entire_config:
            match_interface_name = junos_ipv6_interface_re.match(line)
            if match_interface_name:
                interface_name = match_interface_name.group(1)
                interface_name.replace("/", "-")
                #print "DEBUG: matched junos ipv6 address line. Interface:", short_interface_name, "IPv6 address:", match_interface_name.group(2)
                print hostname + "-" + interface_name + '.' + environment + '.' + 'linkedin.com' + ' AAAA ' + match_interface_name.group(2)
    continue


































