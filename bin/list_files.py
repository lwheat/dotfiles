"""
Example usage of list_files() API.

NAME:
    list_files

SYNOPSIS:
    list_files(owner)

DESCRIPTION:
    Get a list of the files in the user and shared storage areas.

    Files in the shared storage area are prefixed with 'shared/'

    Arguments:
    owner -- Name of user whose storage area to list files in.  None or '' to
             only list files in shared storage area.

    Return:
    List of file names.

"""
import xmlrpclib
import sys

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

# Check that command-line argument was given.
if len(sys.argv) < 2:
    print >> sys.stderr, 'usage: %s owner' % sys.argv[0]
    sys.exit(1)

owner = sys.argv[1]

print '\nCalling list_files() for user', owner

try:
    files = qm.list_files(owner)
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

print '\n'.join(files)
