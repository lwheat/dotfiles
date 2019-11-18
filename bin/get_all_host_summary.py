"""
Example usage of get_all_host_summary() API.

NAME:
    get_all_host_summary

SYNOPSIS:
    get_all_host_summary()

DESCRIPTION:
    Get a summary of all VM execution hosts known to the server.

    Return:
    Dictionary with host_id as key, and host data dictionary as value.
    {host_id: {}, host_id: {}, ..}
    Each host data dictionary contains the following keys:
    'agent id', 'agent version', 'ip address', 'network name', 'vm count',
    'mem available', 'free cores', 'total cores', 'locked_by'

    The 'locked_by' key will not be present if the host is unlocked.

"""
import xmlrpclib

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

summary = qm.get_all_host_summary()

for host_id, host_info in summary.viewitems():
    print '\nHost %s info:' % host_id
    for k, v in host_info.viewitems():
        print '  %s: %s' % (k,v)

