#!/usr/bin/python
#
# audit_lldp_neighbors.py
#   This initial implementation of the script will only parse JUNOS configurations. The BBRs
#   at LinkedIn only activate LLDP on a per neighbor basis instead of globally. There are instances
#   with active neighbors and LLDP disabled. This script attempts to address this issue
#
#   input: list of filenames to parse; filename must contain hostname eg. lca1-crt01.nw-config.txt
#   output: lists ports enable and not-enable with LLDP
# 

import sys
import re

# site codes
all_sites = ["lca1", "eat1", "ech2", "eda6", "edc2", "ehk1", "ela1", "ela4", "esg3", "esp2", \
             "esv5", "esy1", "idb2", "lor1", "lsg1", "ltx1", "lva1", "tln1", "tmu1", "vmi1"]

# enviornment codes
all_environments = ["nw", "corp", "prod", "corp"]

# remove executable file name from list, leaves list of files
sys.argv.remove(sys.argv[0])

hostname_re = re.compile(r'.*((' + "|".join(all_sites) + r')(.*)\.(' + "|".join(all_environments) + r')).*')
junos_ipv6_interface_re = re.compile(r'^set interfaces (.*) (description|unit \d+ description) ".*crt[01].*"')
junos_protocol_lldp_re = re.compile(r'^set protocols lldp interface (.*)')


for file in sys.argv:

    m = hostname_re.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2) + m.group(3)+ '.' + m.group(4)
        print "hostname:", hostname

    # otherwise, do not process / parse the file
    else:
        print 'WARNING: "' + file + '" does not contain device hostname.'
        continue

    with open(file) as f:
        entire_config = f.readlines()
    for line in entire_config:
        match_int_desc = junos_ipv6_interface_re.match(line)
        match_protocol_lldp = junos_protocol_lldp_re.match(line)
        if match_int_desc:
            interface_name = match_int_desc.group(1)
            print "DEBUG: matched line is '", match_int_desc.group(0), "'"
            print "Interface name:", interface_name
        if match_protocol_lldp:
            protocol_lldp = match_protocol_lldp.group(1)
            print "Interface LLDP:", protocol_lldp 

# if match is Loopback interface, create DNS entry for device 

def write_dns_record_stdout(hostname_str, interface_string, ipv6_address_string):
    # if not the loopback interface
    if interface_string.find("lo") < 0:
        print hostname_str + '-' + interface_string + '.' + environment + '.' + 'linkedin.com' + ' AAAA ' + ipv6_address
    # if this is the loopback interface, create loopback & host records
    else:
        print hostname_str + '.' + environment + '.' + 'linkedin.com' + ' AAAA ' + ipv6_address
        # CNAME for "lo" interface
        print hostname_str + '-' + interface_string + '.' + environment + '.' + 'linkedin.com' + \
                           ' CNAME ' + hostname_str + '.' + environment + '.' + 'linkedin.com.'
