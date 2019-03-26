"""
Example usage of reset_vm_lifetime() API.

NAME:
    reset_vm_lifetime

SYNOPSIS:
    reset_vm_lifetime(owner, vm_id)

DESCRIPTION:
    Reset the amount of time remaining for the VM instance to live.

    Arguments:
    owner -- Name of user making request.  Only VM instances owned by this
             user can be extended.
    vm_id -- VM identifier (UUID string) specifying VM to extend.

    Return:
    True if success.  Raises RuntimeError exception if error.

"""
import xmlrpclib
import sys

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

# Check that command-line arguments are given.
if len(sys.argv) < 3:
    print >> sys.stderr, 'usage: %s username vm_id' % sys.argv[0]
    sys.exit(1)

owner = sys.argv[1]
vm_id = sys.argv[2]

#print '\nCalling reset_vm_lifetime() for VM instance:', vm_id

try:
    vm_ids = qm.reset_vm_lifetime(owner, vm_id)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

#print 'Reset time to live for vm instance:', vm_id
