"""
Example usage of get_host_stats() API.

NAME:
    get_host_stats

SYNOPSIS:
    get_host_stats(host_id)

DESCRIPTION:
    Get stats for the specified host.

    The following stats information is returned: uptime, disk usage, CPU load,
    and memory usage.  Each of these stats is returned as a separate
    dictionary.  Each dictionary has the following keys:

    uptime keys: days, hours, minutes
    disk_usage keys: mount_point
    cpu_load: one, five, fifteen
    memory_usage keys: free, used, total, swapped, swap_total, available

    The value of the disk_usage is a dictionary containing the followin keys:
    partition, blocks, used, available, capacity.

    The items in the cpu_load dictionary refer to the average CPU load over the
    last one, five, and ten minutes.

    Arguments:
    host_id -- ID of host (IP address) to get stats for.

    Return: Dictionary of stats info dictionaries.  Top-level dictionary has
    the following keys: uptime, disk_usage, cpu_load, memory_usage

"""
import xmlrpclib
import sys

qm = xmlrpclib.ServerProxy('http://qmanager.rtp.ci.spirentcom.com:8080')

# Check that command-line argument was given.
if len(sys.argv) < 2:
    print >> sys.stderr, 'usage: %s host_id' % sys.argv[0]
    sys.exit(1)

host_id = sys.argv[1]

print '\nCalling get_host_stats() for host:', host_id

try:
    stats = qm.get_host_stats(host_id)
    print stats
except Exception, ex:
    print >> sys.stderr, 'ERROR:', ex
    sys.exit(1)

all_stats = []

# Get uptime
up = stats['uptime']
title = 'Uptime:'
st = [title]
st.append('-'*len(title))
st.append('Up for %s days, %s hours and %s minutes\n'\
          % (up['days'], up['hours'], up['minutes']))
all_stats.append('\n'.join(st))

# Get disk usage
disks = stats['disk_usage']
title = 'Disk Usage:'
st = [title]
st.append('-'*len(title))
for mount, disk_info in disks.viewitems():
    st.append('Usage for: %s' % mount)
    for k, v in disk_info.viewitems():
        st.append('  %s: %s' % (k, v))
    st.append('')
all_stats.append('\n'.join(st))

# Get CPU load
load_stats = stats['cpu_load']
title = 'CPU Load Average:'
st = [title]
st.append('-'*len(title))
st.append('last one minute: %s' % load_stats['one'])
st.append('last five minutes: %s' % load_stats['five'])
st.append('last fifteen minutes: %s\n' % load_stats['fifteen'])
all_stats.append('\n'.join(st))

# Get Memory Usage
memory_usage = stats['memory_usage']
title = 'Memory usage:'
st = [title]
st.append('-'*len(title))
for k, v in memory_usage.viewitems():
    st.append('%s: %s' % (k, v))
all_stats.append('\n'.join(st))

print '\n'.join(all_stats), '\n'
