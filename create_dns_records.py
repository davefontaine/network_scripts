#!/usr/bin/python

import sys
import re
from ciscoconfparse import CiscoConfParse

all_sites = ["lca1", "lva1"]
all_environments = ["nw", "corp", "prod"]
interface_name_mapping = {
    'Loopback':'lo',
    'Ethernet':'eth',
    'GigabitEthernet':'ge',
    'TenGigabitEthernet':'te',
    'Vlan':'vlan',
    'xe':'xe'
}

# remove executable file name from list
sys.argv.remove(sys.argv[0])

# build regexp for matching hostname in file name
all_sites_re = "|".join(all_sites)
all_environments_re = "|".join(all_environments)
search_string = r'.*((' + all_sites_re + r')(.*)\.(' + all_environments_re + r')).*'

p = re.compile(search_string)
ipv6_address_re = re.compile(r".*ipv6 address\W(.*)/[0-9]+")
interface_name_re = re.compile(r"^interface ([a-zA-Z]+)([0-9]+)/?([0-9]+)?/?([0-9]+)?")

for file in sys.argv:
    m = p.match(file)
    if m:
        hostname = m.group(2)+m.group(3)
        environment= m.group(4)
    else:
        continue
    f = CiscoConfParse(file)
    interfaces = f.find_objects(r"^interface")
    interfaces = f.find_objects_w_child(parentspec=r"^interface", childspec=r"ipv6 address")
    for interface_name in interfaces:
        match_interface_name = interface_name_re.match(interface_name.text)
        short_interface_name = interface_name_mapping[match_interface_name.group(1)]
        dns_name = hostname + "-" + short_interface_name
        if match_interface_name.lastindex >= 2:
            dns_name += '-' + match_interface_name.group(2)
        if match_interface_name.lastindex >= 3:
            dns_name += "-" + match_interface_name.group(3)
        if match_interface_name.lastindex >= 4:
            dns_name += "-" + match_interface_name.group(4)
        dns_name += '.' + environment + '.' + 'linkedin.com'
        for child in interface_name.children:
            match_ipv6_address = ipv6_address_re.match(child.text)
            if match_ipv6_address:
                ipv6_address = match_ipv6_address.group(1)
                dns_record = dns_name + ' AAAA ' + ipv6_address
                print dns_record









