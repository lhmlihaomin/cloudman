#!/usr/bin/python
#coding:utf-8

"""Update service version on Qcloud CVM instances.
"""
import re
import os

from scp import SCPClient

from ssh import SshHandler


def run_cmd(ssh_client, cmd):
    print "----------------------------------------"
    print "CMD:"
    print "    "+cmd
    exitcode, stdout, stderr = ssh_client.run(cmd)
    print "OUTPUT:"
    print stdout
    print "----------------------------------------"


# Local parameters:
PACKAGE_DIR = ".\\packages"
PEM_DIR = ".\\pem"

# Module parameters:
MODULE_NAME = "fakedjango"
OLD_VERSION = "1.0.0"
NEW_VERSION = "1.0.5"

# Remote parameters
host = {
    'ip': '192.168.204.134',
    'username': 'lhm',
    'key_name': 'key1'
}

p = "^{0}-(CN|EN|MF)-{1}-[-0-9]+.tar.gz".format(MODULE_NAME, NEW_VERSION)
for fname in os.listdir(PACKAGE_DIR):
    if re.match(p, fname) is not None:
        package_file = os.path.sep.join([PACKAGE_DIR, fname])
        break

module_path = "/home/{0}/cloud-{1}".format(host['username'], MODULE_NAME)
service_path_old = "{0}/cloud-{1}-{2}".format(module_path, MODULE_NAME, OLD_VERSION)
service_path_new = "{0}/cloud-{1}-{2}".format(module_path, MODULE_NAME, NEW_VERSION)

# connect to host SSH server:
ssh = SshHandler(host['ip'], host['username'], host['key_name'], PEM_DIR)

print "Checking module path:"
cmd = "ls {0}".format(module_path)
run_cmd(ssh, cmd)

raw_input("Press Enter to continue ...")
# copy new version package:
print "# Copying ", package_file, " --> ", module_path
scp = SCPClient(ssh.client.get_transport())
scp.put(package_file, module_path)

cmd = "ls {0}".format(module_path)
run_cmd(ssh, cmd)

raw_input("Press Enter to continue ...")
# extract new version package:
print "# Extracting package:"
cmd = "tar -C {0} -xzf {1}/{2}".format(module_path, module_path, fname)
run_cmd(ssh, cmd)

cmd = "ls {0}".format(module_path)
run_cmd(ssh, cmd)

raw_input("Press Enter to continue ...")
# modify autostart script:
print "# Editing startup script ..."
cmd = "sudo sed -i 's/{0}-{1}-{2}/{0}-{1}-{3}/g' /etc/rc.local".format(
    'cloud', 
    MODULE_NAME, 
    OLD_VERSION, 
    NEW_VERSION
    )
run_cmd(ssh, cmd)

raw_input("Press Enter to continue ...")
# stop old version service:
print "# Stopping old version:"
cmd = "cd {0}/bin&&./stop.sh".format(service_path_old)
run_cmd(ssh, cmd)

cmd = "curl localhost:12345/"
run_cmd(ssh, cmd)

raw_input("Press Enter to continue ...")
# start new version service:
print "# Starting new version:"
cmd = "cd {0}/bin&&./start.sh".format(service_path_new)
run_cmd(ssh, cmd)

# check new version process:
cmd = "curl localhost:12345/"
run_cmd(ssh, cmd)

# remove tarball:
cmd = "rm {0}/{1}".format(module_path, fname)
run_cmd(ssh, cmd)
