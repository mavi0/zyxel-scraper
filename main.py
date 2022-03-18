import paramiko
import cmd
import time
import sys

buff = ''
resp = ''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.1', username='admin', password='18f1f667')
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
chan = ssh.invoke_shell()

# turn off paging
chan.send('terminal length 0\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
#print (''.join(output))

# Display output of first command
chan.send('atcmd /dev/ttyUSB3 at+qeng=\"servingcell\"')
chan.send('\n')
time.sleep(1)
resp = chan.recv(9999)
output = resp.decode('ascii').split(',')
print (''.join(output))

# Display output of second command
# chan.send('sh ver')
# chan.send('\n')
# time.sleep(1)
# resp = chan.recv(9999)
# output = resp.decode('ascii').split(',')
# print (''.join(output))

ssh.close()  