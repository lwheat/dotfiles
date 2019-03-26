"""
Example usage of stop_vm() API.

NAME:
    stop_vm

SYNOPSIS:
    stop_vm(owner, vm_id, save_image, save_name)

DESCRIPTION:
    Stop the specified VM instance.

    Arguments:
    owner     -- Name of user making request.  Only VM instances owned by this
                 user can be stopped.
    vm_id     -- VM identifier (UUID string) specifying VM to stop.  If 'all'
                 is given, then all VM instances for the owner are stopped.
    save_vm   -- True to save the VM image file and transfer it back to the
                 server.  False (default) to delete image when done.
    save_name -- Optional name to use for saving VM image.  If name is None
                 (default), then VM ID + original VM file name is used.
                 This argument is ignored if save_vm is False.

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

print '\nCalling stop_vm() to stop VM instance:', vm_id

try:
    qm.stop_vm(owner, vm_id)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

print 'Stopped vm instance:', vm_id

