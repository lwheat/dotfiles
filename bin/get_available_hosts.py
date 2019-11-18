"""
Example usage of get_get_available_hosts() API.

NAME:
    get_available_hosts()

SYNOPSIS:
    get_available_hosts()

DESCRIPTION:
    Get a list VM execution hosts available to the QManager server.

    Use this API instead of get_all_host_summary() when only a list of
    available hosts is required, as it is much more efficient.

"""
import xmlrpclib

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

for host in qm.get_available_hosts():
    print 'Host:', host

