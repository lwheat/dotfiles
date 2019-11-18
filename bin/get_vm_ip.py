"""
Example usage of get_vm_ip() API.

NAME:
    get_vm_ip

SYNOPSIS:
    get_vm_ip(vm_id)

DESCRIPTION:
   Get the IP address of the specified VM instance.

   If VM not finished starting yet, then the string 'unknown' is returned.  If
   agent cannot get IP address of a STCv instance, then the string 'failed' is
   returned.  If agent cannot get IP address of a generic instance, then the
   string 'N/A' is returned.

   An IP address will not be available unitl at least 60 seconds after starting
   a VM instance.

   Arguments:
   vm_id -- ID of VM instance to get IP address of.

   Return:
   IP address string of VM.
   'unknown' if still waiting for VM to acquire IP.
   'failed' if cannot get STCv IP address.
   'N/A' if cannot get generic VM IP address.

"""
import xmlrpclib
import sys

#qmanagerLocation = 'cal'
qmanagerLocation = 'rtp'
qm = xmlrpclib.ServerProxy('http://qmanager.%s.ci.spirentcom.com:8080' % (qmanagerLocation))

# Check that command-line argument was given.
if len(sys.argv) < 2:
    print >> sys.stderr, 'usage: %s vm_id' % sys.argv[0]
    sys.exit(1)

vm_id = sys.argv[1]

#print 'Calling get_vm_ip() for VM instance:', vm_id,

try:
    vm_ip = qm.get_vm_ip(vm_id)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

#print 'IP address for VM:', vm_ip
print 'VM instance:', vm_id, 'IP address:', vm_ip
