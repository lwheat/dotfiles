"""
Example usage of start_stc_vm() API.

NAME:
    start_stc_vm

SYNOPSIS:
    vm_id_list = start_stc_vm(
        user_name, vm_image=None, ttl_minutes=None, use_socket=False,
        vm_desc=None, instances=2, host_id=None, share_vlan=True, vlan_id=None,
        vm_mem=None, cores=None, use_ext_net=False, ntp_server=None,
        license_server=None, prefer_busy=None, static_ip=None, netmask=None,
        gateway=None)

    Default parameter values are shown above.  Passing a value of None will
    result in the default value being used.

DESCRIPTION:
    Start one or more STCv VM instances on the same host.

    If an image file name is prefixed with 'shared/' this specifies to use that
    image from the shared storage area.

    Arguments:
    user_name     -- Name of user launching VM instance.
    vm_image      -- Name of image file or build number.  If None, then use the
                     latest file in storage.  If parameter starts with '#',
                     then a build number is indicated instead, and the
                     corresponding STCv image is fetched from the build server.
    ttl_minutes   -- Minutes before the VM is automatically stopped.  If set to
                     None (default), then use configured default value.
    use_socket    -- If True, connect VM instances with socket.  If False
                     (default) or None then connect VM instances using vbridge.
    vm_desc       -- Text describing VM instance.
    instances     -- Number of VM instances to start with this config.  If set
                     to None then use the default of 2 instances.
    host_id       -- ID of host to start VM instance on.  If None (default),
                     then select the best host (see prefer_busy) from hosts
                     that are available to the user.
    share_vlan    -- If True (default), VM instances will use same VLAN.
    vlan_id       -- VLAN that VM instances will communicate on.  If None,
                     (default) server will allocate unused VLAN from
                     configured range.
    vm_mem        -- MB of memory to allocate to each VM instance.  If set
                     to None, then agent's default value (usually 512M) is
                     used.
    cores         -- Number of logical CPUs to use for each VM instance.  If
                     set to None, then use 1 core.  If set to True, then use
                     default maximum cores of STCv.  If set to a positive
                     integer value, then use that number of cores.
    use_ext_net   -- If True, use external network interface to connect VM
                     instances running on separate hosts.  VLAN ID must be
                     specified to connect to existing remote VM instances.
                     Target host must have agent configured wit test
                     interface (check with system admin).
    ntp_server    -- IP address or DNS name of NTP server for STCv instance to
                     use.  If None (default), use configured server.
    license_server -- IP address or DNS name of license server.  None to
                      use default license server specified in server
                      configuration.
    prefer_busy   -- If True, prefer hosts with least remaining CPU.  Default
                     as per server config.  Ignored if host_id specified.
    static_ip     -- IP address to use for VM.  IF None, then use DHCP.
    netmask       -- Netmask for VM.  Ignored if static_ip is None.
    gateway       -- Network gateway for VM.  Ignored if static_ip is None.

    Return:
    List of VM ID values for started VM instances.


    NOTE: Since keyword-arguments are not supported by XMLRPC, a value of None
    must be given for any defaulted arguments preceding a specified argument.
    For example, specifying vlan_id with value 2701:
    vm_ids = qm.start_vm(user_name, '#4.20.1653', None, None, None, None, None,
                         None, 2701)

    Note on cores:
    ----------------
    STCv will work with multiple CPUs.  Optimal performance can be seen using 3
    vCPUs.  Ideally they would be pinned to dedicated logical cores.  With 3
    vCPUs the VM will allocate 1 CPU each to the sFPGA Analyzer, sFPGA
    Generator, and FW.

    The VM pins the processes to CPUs, and will only pin to 3.  Although
    additional cores can be specified, then may have little or no effect.

"""
import xmlrpclib
import sys

qmanagerLocation = 'rtp'
qm = xmlrpclib.ServerProxy('http://qmanager.%s.ci.spirentcom.com:8080' % (qmanagerLocation),
                           allow_none=True)

# Check that command-line arguments are given.
argc = len(sys.argv)
if argc < 3:
    msg = (
        'usage: %s user_name vm_image [ttl_minutes] [vlan_ids]\n'
        'To specify a build number, the first character vm_image must be "#"\n'
        'Example: python start_stc_vm_api_example.py jdoe \'#4.10.0334\''
         % sys.argv[0])
    print >> sys.stderr, msg
    sys.exit(1)

user_name = sys.argv[1]
vm_image = sys.argv[2] if argc >= 3 else None
ttl_minutes = int(sys.argv[3]) if argc >= 4 else None
vlan_ids = map(int, sys.argv[4].split()) if argc >= 5 else None
vm_mem = 2048 * (len(vlan_ids) if vlan_ids != None else 1)

#print '\nCalling start_vm() to start VM instances on %s QManager' % (qmanagerLocation.upper())

try:
    vm_ids = qm.start_stc_vm(user_name, vm_image, ttl_minutes, False, "stc vm", 2, None, True, vlan_ids, vm_mem)
    #print 'Started new vm instances:\n  %s' % ('\n  '.join(vm_ids),)
    print ' '.join(vm_ids)
except Exception as ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)
