"""
Example usage of get_active_vms() API.

NAME:
    get_active_vms

SYNOPSIS:
    get_active_vms(host_ids)

DESCRIPTION:
    Get the active VM instances for the specified hosts, or all hosts.

    Arguments:
    host_ids -- List of hosts to get VM instances for.  If None (default)
                then get VM instances for all hosts.

    Return:
    List of dictionaries [{}, {}, ..].  Each dictionary contains the
    following keys:
        host_id, owner, vm_id, server_image_file, vlan_id, vm_ip, run_time,
        server_image_file, vm_type, run_time, time_to_live

    The following keys are present if they have a value:
        telnet_port, vnc_port, vm_desc

"""
import xmlrpclib
import sys

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

active_vms = qm.get_active_vms()
me = "lwheat"
meKey = "owner"
vmKey = "vm_id"
myVMs = []

#print 'Active VM instances:'
if (len(sys.argv) > 1):
    me = sys.argv[1]

for avm in active_vms:
    if (meKey in avm.keys() and avm[meKey] == me and vmKey in avm.keys()):
        myVMs.append("%s:%s" % (avm[vmKey], avm["image_src"]))
    #for k,v in avm.viewitems():
    #    print '  %s: %s' % (k,v)
    #print
print ' '.join(myVMs)
