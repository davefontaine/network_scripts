#!/usr/bin/python
#
# convert_64_to_128.py
#   input: list of filenames to parse; filename must contain hostname eg. lca1-crt01.nw-config.txt
#   output: replaces /64 on p2p links with /126 (not on VLANs which remain /64)
#         in other words, the following is done
#
#         interface Ethernet 1/2
#           no ipv6 address face:b00c::1/64
#           ipv6 address face:b00c::1/126
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
    'loopback':'lo',
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


for file in sys.argv:

    m = hostname_re.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2) + m.group(3) + m.group(4) +".linkedin.com"
        print
        print "# ", hostname
        print
        print "config t"

    # otherwise, do not process / parse the file
    else:
        print
        print 'WARNING: "' + file + '" does not contain device hostname.'
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

            # find "ipv6 address" under interface and grab address
            for subinterface_line in interface_name.children:
                match_ipv6_address = ipv6_address_re.match(subinterface_line.text)
                if match_ipv6_address:
                    if match_interface_name.group(1) == "Vlan"\
                    or match_interface_name.group(1) == "Loopback"\
                    or match_interface_name.group(1) == "loopback":
                        print "# Skipping " + match_interface_name.group(0)
                        continue
                    ipv6_address = match_ipv6_address.group(1)
                    print match_interface_name.group(0)
                    print "  no ipv6 address " + ipv6_address + "/64"
                    print "  ipv6 address " + ipv6_address + "/126"
    print "end"
    print 
    continue


































