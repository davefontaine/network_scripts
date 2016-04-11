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

# build regexp for matching hostname in file name
all_sites_re = "|".join(all_sites)
all_environments_re = "|".join(all_environments)
filename_re_search_string = r'.*((' + all_sites_re + r')(.*)\.(' + all_environments_re + r')).*'

p = re.compile(filename_re_search_string)
ipv6_address_re = re.compile(r".*ipv6 address\W(.*)/[0-9]+")
interface_name_re = re.compile(r"^interface ([a-zA-Z]+)([0-9]+)/?([0-9]+)?/?([0-9]+)?")

# incomplete items
# if match is Loopback interface, create DNS entry for device 

# def write_dns_record(short_inteface_name, 

for file in sys.argv:

    m = p.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2)+m.group(3)
        environment= m.group(4)

    # otherwise, do not process / parse the file
    else:
        continue

    # parse the file
    parsed_file = CiscoConfParse(file)

    # pull out all interfaces which have an ipv6 address
    interfaces = parsed_file.find_objects_w_child(parentspec=r"^interface", childspec=r"ipv6 address")

    # for every interface that matches the above conditions, 
    #  - process the interface name 
    #  - convert it to DNS-style string
    #  - print DNS entry
    for interface_name in interfaces:
        match_interface_name = interface_name_re.match(interface_name.text)
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

        # if loopback interface, generate dns host entry for device
        else:
            dns_name = hostname

        # append FQDN string to dns entry
        dns_name += '.' + environment + '.' + 'linkedin.com'

        # find "ipv6 address" under interface and grab address
        for subinterface_line in interface_name.children:
            match_ipv6_address = ipv6_address_re.match(subinterface_line.text)
            if match_ipv6_address:
                ipv6_address = match_ipv6_address.group(1)

        # create record by merging dns_name and ipv6 address and write entry to stdout
        dns_record = dns_name + ' AAAA ' + ipv6_address
        print dns_record

































