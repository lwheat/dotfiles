"""
Example usage of start_generic_vm() API.

NAME:
    start_generic_vm

SYNOPSIS:
    vm_id_list = start_generic_vm(
        user_name, instances, vm_image_file, host_id, cores, vm_mem,
        vm_ttl_sec, vnc_cons, telnet_cons, vm_desc):

DESCRIPTION:
    Start one or more non-STCv VM instances.

    If an image file name is prefixed with 'shared/' this specifies to use that
    image from the shared storage area.

    Arguments:
    user_name     -- Name of user launching VM instance.
    instances     -- Number of VM instances to start with config params.
    vm_image_file -- Name of image file.  If None, then use latest file in
                     storage.
    host_id       -- ID of host to start VM instance on.  If None, then
                     select the best (least busy) host from hosts that are
                     available to the user.
    cores         -- Number of logical CPUs to use for each VM instance.
    vm_mem        -- MB of memory to allocate to each VM instance.  If set
                     to None, then agent's default value (usually 512M) is
                     used.
    vm_ttl_sec    -- Seconds before the VM is automatically stopped.  If
                     set to None (default) or 0, the Agent's default value
                     of 3 days is used.
    vnc_cons      -- Use VNC to access console.  Default is False.
    telnet_cons   -- Use telnet to access console.  Default is True.
    vm_desc       -- Text describing VM instance.  Default is None.
    cdrom_iso     -- ISO file to use as VM CDROM.  Default is None.
    prefer_busy   -- If True, prefer hosts with least remaining CPU.
                     Default False.  Ignored if host_id specified.

    Return:
    List of VM ID values for started VM instances.

"""
import xmlrpclib
import sys

SECONDS_PER_DAY = 60 * 60 * 24

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080',
                           allow_none=True)

# Check that command-line arguments are given.
if len(sys.argv) < 3:
    print >> sys.stderr, 'usage: %s user_name vm_image_file' % sys.argv[0]
    sys.exit(1)

user_name = sys.argv[1]
vm_image_file = sys.argv[2]
vm_ttl_sec = (int(sys.argv[3]) if len(sys.argv) > 3 else 14) * SECONDS_PER_DAY
instances = (int(sys.argv[4]) if len(sys.argv) > 4 else 1)
host_id = sys.argv[5] if len(sys.argv) > 5 else None
cores = 2
vm_mem = 2048

#print '\nCalling start_generic_vm() to start VM instance:', vm_image_file

try:
    # Start 1 instance.
    vm_ids = qm.start_generic_vm(user_name, instances, vm_image_file, host_id, cores, vm_mem, vm_ttl_sec)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

#print 'Started new vm instance:\n  %s' % ('\n  '.join(vm_ids),)
print ' '.join(vm_ids)
