#!/usr/bin/python
#
#  dfontain-mn1:network_scripts dfontain$ ./test_paramiko.py
#  Password:
#  Traceback (most recent call last):
#    File "./test_paramiko.py", line 12, in <module>
#      remote_conn_pre.connect(ip_addr, username=username, password=password, look_for_keys=False, allow_agent=False)
#    File "/Library/Python/2.7/site-packages/paramiko/client.py", line 311, in connect
#      raise NoValidConnectionsError(errors)
#
#  can't ssh from laptop using ip address
#
#     dfontain-mn1:python dfontain$ ssh 10.252.128.4
#     ssh: connect to host 10.252.128.4 port 22: Connection refused
#
#  running this on lca1-netops01.corp.linkedin.com produces no errors (using ip address)
#  running with FQDN works fine however from laptop too
#
#     dfontain-mn1:python dfontain$ ssh lca1-c1-csw01-lo0.nw.linkedin.com

#   BY ACCESSING THIS SYSTEM YOU ARE ENTERING INTO AN AGREEMENT.
#   By continuing your login, you agree that:

import paramiko
from getpass import getpass

ip_addr = 'lca1-c1-csw01-lo0.nw.linkedin.com'
username = 'dfontain'
password = getpass()

remote_conn_pre=paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(ip_addr, username=username, password=password, look_for_keys=False, allow_agent=False)

remote_conn = remote_conn_pre.invoke_shell()
outp = remote_conn.recv(5000)

# send command
remote_conn.send("show version\n")
outp = remote_conn.recv(5000)
print outp



