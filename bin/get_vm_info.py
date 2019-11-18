"""
Example usage of get_vm_info() API.

NAME:
    get_vm_info

SYNOPSIS:
    get_vm_info(vm_id)

DESCRIPTION:
   Get information about the specified VM instance.

   Arguments:
   vm_id -- ID of VM instance to get information for.

   Return:
   Dictionary of VM information having the following keys:
       vm_id, host_id, vm_type, owner, server_image_file, vlan_id, vm_ip,
       vm_network, image_src, run_time, time_to_live, vm_desc,
       telnet_port, vnc_port

"""
import xmlrpclib
import sys

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

# Check that command-line argument was given.
if len(sys.argv) < 2:
    print >> sys.stderr, 'usage: %s vm_id' % sys.argv[0]
    sys.exit(1)

vm_id = sys.argv[1]

print '\nCalling get_vm_info() for VM instance:', vm_id

try:
    vm_info = qm.get_vm_info(vm_id)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

print 'Information for VM', vm_id
for k,v in vm_info.viewitems():
    print '  %s: %s' % (k,v)
print
