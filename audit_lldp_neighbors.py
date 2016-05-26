#!/usr/bin/python
#
# audit_lldp_neighbors.py
#   This initial implementation of the script will only parse JUNOS configurations. The BBRs
#   at LinkedIn only activate LLDP on a per neighbor basis instead of globally. There are instances
#   with active neighbors and LLDP disabled. This script attempts to address this issue
#
#   input: list of filenames to parse; filename must contain hostname eg. lca1-crt01.nw-config.txt
#   output: lists ports enabled and not-enabled with LLDP

# Try this to see if excluding EXT will work:
#   egrep "^set interfaces.*description" * | egrep -v "\|EXT\|"



import sys
import re

# site codes for all BBRs
all_sites = ["lca1", "eat1", "ech2", "eda6", "edc2", "ehk1", "ela1", "ela4", "esg3", "esp2", \
             "esv5", "esy1", "idb2", "lor1", "lsg1", "ltx1", "lva1", "tln1", "tmu1", "vmi1"]

# strings to exclude from interface description matches
interface_description_excluded_items = ['\|EXT\|', 'RESV_', 'ae\d+', 'fxp\d+', ' unit ', '\.gts']

# enviornment codes
all_environments = ["nw", "corp", "prod", "corp"]

# remove executable file name from list, leaves list of files
sys.argv.remove(sys.argv[0])
list_of_files = sys.argv

hostname_re = re.compile(r'.*((' + "|".join(all_sites) + r')(.*)\.(' + "|".join(all_environments) + r')).*')
junos_ipv6_interface_re = re.compile(r'^set interfaces (.*) (description|unit \d+ description).*')
junos_protocol_lldp_re = re.compile(r'^set protocols lldp interface (.*)')


for file in list_of_files:

    m = hostname_re.match(file)

    # if the filename conforms to the hostname naming convention, make assignments
    if m:
        hostname = m.group(2) + m.group(3)+ '.' + m.group(4)
        print "hostname:", hostname

    # otherwise, do not process / parse the file
    else:
        print 'WARNING: "' + file + '" does not contain device hostname.'
        continue

    # open a file to write the hostname-specific configuration

    with open(file) as f:
        entire_config = f.readlines()
    for line in entire_config:
        match_int_desc = junos_ipv6_interface_re.match(line)
        if match_int_desc:
            entire_line = match_int_desc.group(0)
            interface_name = match_int_desc.group(1)
            excluded_lines = '(' + "|".join(interface_description_excluded_items) + ')'
            # if the interface description matches CRT but not the excluded items, generate config
            if not re.search(excluded_lines, entire_line) and re.search('-crt\d+', entire_line):
                print entire_line.rstrip('\r\n') + ' ---> ' + interface_name





