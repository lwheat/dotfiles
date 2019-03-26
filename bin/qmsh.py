"""
Spirent TestCenter Command Shell

Interactive command shell that provides Session Manager and Automation API
functionality using a command line interface.  This command accesses a
TestCenter Server over its HTTP interface, so no local BLL installation is
needed.

Type help to see help info.  Use <TAB> for command auto-completion.

"""
from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Andrew Gillis'

import sys
import socket
import cmd
import xmlrpclib
import re
import fnmatch
import readline
import datetime

if sys.hexversion < 0x03000000:
    input = raw_input

__version__ = '1.0.0'
__description__ = 'QManager Command Shell (qmsh)'
__author__ = 'Andrew J. Gillis'


class QManagerCommandShell(cmd.Cmd):

    intro = 'Welcome to ' + __description__
    _qm = None
    _user = None
    _server = None

    def preloop(self):
        # Do this once before entering command loop.
        #self._update_sessions()
        self.postcmd(None, None)

    def postcmd(self, stop, line):
        # Do this after executing each command.
        if self._user:
            self.prompt = '%s:%s> ' % (self._server, self._user)
        else:
            self.prompt = '%s:> ' % (self._server,)
        return stop

    def do_version(self, args):
        """Show qmsh version."""
        print(__description__, 'version', __version__)

    def do_exit(self, s):
        """Exit the QManager shell."""
        return True

    do_quit = do_exit

    ###########################################################################
    # Login/logout commands
    #

    def do_login(self, login):
        """Login with the specified user name."""
        if not login:
            print('please supply a user name to login')
            return
        self._user = re.sub(r'\W', '_', str(login).strip().lower())
        print('Logged in as:', self._user)

    def do_logout(self, args):
        """Logout current user."""
        self._user = None

    ###########################################################################
    # VM information commands
    #

    def do_lsvm(self, args):
        """List running VM instances.

        lsvm [-l] [-h host] [-i image] [-u user_name] [-v vlan] [host_ip ..]

        OPTIONS:

        -l
            Show detailed information for each VM.

        -g
            Show only generic type VMs.

        -s
            Show only STCv type VMs.

        -i image, --image image
            Show only VMs running specified image.  The image will either be a
            build number, such as 4.50.5426, or an image file name.

        -u user_name, --user user_name
            Show only VMs belonging to specified user.

        -v vlan, --vlan vlan
            Show only VMs on specified VLAN.

        --mine
            Show only VMs belonging to the currently logged in user.

        """
        l_opt = False
        hosts = None
        img_opt = owner_opt = type_opt = vlan_opt = None
        if args:
            args = args.split()
            missing_arg = 'missing value after'
            while args:
                arg = args.pop(0)
                if arg == '-l':
                    l_opt = True
                elif arg == '-g':
                    type_opt = 'generic'
                elif arg == '-s':
                    type_opt = 'stc'
                elif arg in ('-i', '--image'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    img_opt = args.pop(0)
                elif arg in ('-u', '--user'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    owner_opt = args.pop(0)
                elif arg in ('-v', '--vlan'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    vlan_opt = int(args.pop(0))
                elif arg == '--mine':
                    if not self._user:
                        print('login required for', arg, file=sys.stderr)
                        return
                    owner_opt = self._user
                elif arg[0] == '-':
                    print('unrecognized argument:', arg, file=sys.stderr)
                    return
                else:
                    args.insert(0, arg)
                    hosts = args
                    break

        if hosts:
            print('---> hosts:', hosts)
            active_vms = self._qm.get_active_vms(hosts)
        else:
            active_vms = self._qm.get_active_vms()

        print('Active VM instances:')
        keep = []
        while active_vms:
            avm = active_vms.pop()
            if type_opt and avm.get('vm_type') != type_opt:
                continue
            if vlan_opt and avm.get('vlan_id') != vlan_opt:
                continue
            if owner_opt and avm.get('owner') != owner_opt:
                continue
            if img_opt and avm.get('image_src') != img_opt:
                continue
            keep.append(avm)

        for avm in keep:
            img = avm.pop('image_src')
            vlan = avm.pop('vlan_id')
            vmip = avm.pop('vm_ip')
            owner = avm.pop('owner')
            running = datetime.timedelta(seconds=int(avm.pop('run_time')))
            if not vmip:
                vmip = self._qm.get_vm_ip(avm['vm_id'])
            print('%-15s  %-4s  %s  %s (%s)' %
                  (vmip, vlan, img, owner, running))
            if l_opt:
                for k, v in avm.viewitems():
                    print('  %s: %s' % (k,v))
                print()

    ###########################################################################
    # Hypervisor host commands
    #

    def do_lsh(self, args):
        """List hypervisor hosts.

        lsh [-l] [host_ip]

        OPTIONS:
        -l    Show detailed information for each host.

        """
        l_opt = False
        host_ip = None
        if args:
            args = args.split()
            arg = args.pop(0)
            if arg == '-l':
                l_opt = True
                if args:
                    host_ip = args.pop(0)
            else:
                host_ip = arg

        if host_ip:
            if l_opt:
                summary = self._qm.get_all_host_summary()
                if host_ip in summary:
                    host_info = summary[host_ip]
                    hn = socket.gethostbyaddr(host_ip)[0]
                    print('%s (%s)' % (host_ip, hn))
                    for k, v in host_info.viewitems():
                        print('  %s: %s' % (k,v))
                else:
                    print('host not found')
            else:
                if host_ip in self._qm.get_available_hosts():
                    hn = socket.gethostbyaddr(host_ip)[0]
                    print('%s (%s)' % (host_ip, hn))
                else:
                    print('host not found')
            return

        if l_opt:
            summary = self._qm.get_all_host_summary()
            for host_ip, host_info in summary.viewitems():
                hn = socket.gethostbyaddr(host_ip)[0]
                print('%s (%s)' % (host_ip, hn))
                for k, v in host_info.viewitems():
                    print('  %s: %s' % (k,v))
                print()
        else:
            for host_ip in self._qm.get_available_hosts():
                hn = socket.gethostbyaddr(host_ip)[0]
                print('%s (%s)' % (host_ip, hn))

    def complete_lsh(self, text, line, begidx, endidx):
        return self._complete_hosts(text)

    def do_hostinfo(self, args):
        """Show information about the specified hypervisor host.

        hostinfo [-cdmu] host_name_or_ip

        Information is shown in the order that options are given in.

        EXAMPLES:

        hostinfo -cm 10.109.25.161
        hostinfo qmagent-01.calenglab.spirentcom.com

        OPTIONS:

        -c, --cpu
            Show CPU load averages over 1, 5, and 15 minutes.

        -d, --disk
            Show disk usage for each partition.

        -m, --memory
            Show memory usage statistics.

        -u, --uptime
            Show uptime statistics.

        """
        host = opts = None
        if args:
            args = args.split()
            host = args.pop()

        if not host:
            print('Usage: hostinfo [-cdmu] host_name_or_ip')
            print('    uptime and load stats returned if no options specified')
            return

        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('cannot resolve', host, file=sys.stderr)
            return

        opts = []
        while args:
            arg = args.pop(0)
            if arg.startswith('--'):
                if arg == '--cpu':
                    opts.append('c')
                elif arg == '--disk':
                    opts.append('d')
                elif arg == '--memory':
                    opts.append('m')
                elif arg == '--uptime':
                    opts.append('u')
                else:
                    print('unrecognized option:', arg, file=sys.stderr)
                    return
            else:
                if arg[0] == '-':
                    for ch in arg[1:]:
                        if ch in ('cdmu') and ch not in opts:
                            opts.append(ch)
                        else:
                            print('unrecognized option:', ch, file=sys.stderr)
                            return

        stats = self._qm.get_host_stats(ip)

        if not opts:
            # Get uptime and load averages.
            up = stats['uptime']
            load = stats['cpu_load']
            print('Up for %s days, %s hours, %s minutes, '
                  'load averages: %s, %s, %s'
                  % (up['days'], up['hours'], up['minutes'], load['one'],
                     load['five'], load['fifteen']))
            return

        all_stats = []
        for opt in opts:
            if opt == 'd':
                # Get disk usage.
                disks = stats['disk_usage']
                st = ['Disk Usage:']
                for mount, disk_info in disks.viewitems():
                    st.append('  Usage for: %s' % mount)
                    for k, v in disk_info.viewitems():
                        st.append('    %s: %s' % (k, v))
                all_stats.append('\n'.join(st))
                all_stats.append('')
            elif opt == 'c':
                # Get CPU load.
                load_stats = stats['cpu_load']
                st = ['CPU Load Average:']
                st.append('  last one minute: %s' % load_stats['one'])
                st.append('  last five minutes: %s' % load_stats['five'])
                st.append('  last fifteen minutes: %s' % load_stats['fifteen'])
                all_stats.append('\n'.join(st))
                all_stats.append('')
            elif opt == 'm':
                # Get Memory Usage.
                memory_usage = stats['memory_usage']
                st = ['Memory usage:']
                for k, v in memory_usage.viewitems():
                    st.append('  %s: %s' % (k, v))
                all_stats.append('\n'.join(st))
                all_stats.append('')
            elif opt == 'u':
                # Get uptime.
                up = stats['uptime']
                st = ['Uptime:']
                st.append('  Up for %s days, %s hours and %s minutes'
                          % (up['days'], up['hours'], up['minutes']))
                all_stats.append('\n'.join(st))
                all_stats.append('')

        print('\n'.join(all_stats))

    complete_hostinfo = complete_lsh

    def do_stats(self, args):
        """Show overall usage stats.

        """
        total_cpu = free_cpu = in_use_cpu = 0

        summary = self._qm.get_all_host_summary()
        for host_id, host_info in summary.viewitems():
            host_cpu = int(host_info['total cores'])
            total_cpu += host_cpu
            locked = host_info.get('locked by')
            if locked:
                # If host is locked then all CPUs are in use.
                in_use_cpu += host_cpu
            else:
                free_host_cpu = int(host_info['free cores'])
                in_use_cpu += (host_cpu - free_host_cpu)
                free_cpu += free_host_cpu

        print('total CPU:         ', total_cpu)
        print('used/locked CPU:   ', in_use_cpu)
        print('free CPU:          ', free_cpu)
        capacity = float(in_use_cpu) / float(total_cpu)
        print('capacity used:      %.1f%%' % (capacity * 100,))
        capacity = float(free_cpu) / float(total_cpu)
        print('capacity remaining: %.1f%%' % (capacity * 100,))

    ###########################################################################
    # File and server information commands
    #

    def do_ls(self, args):
        """List files.  Login to see files in the logged in user's storage.

        """
        if args:
            args = args.split()

        try:
            for file_name in self._qm.list_files(self._user):
                if not args:
                    print(file_name)
                else:
                    for a in args:
                        if fnmatch.fnmatch(file_name, a):
                            print(file_name)
                            break
        except Exception, ex:
            print('ERROR:', ex, file=sys.stderr)

    def complete_ls(self, text, line, begidx, endidx):
        return self._complete_files(text)

    def do_cp(self, source_file):
        """Copy the specified file between shared and private storage.

        cp source_file

        Examples:
            cp shared/some_vm.img.gz
            cp my_vm.img.gz

        Prefix the source file with 'shared/' to specify copying from shared
        storage area.  Otherwise, file is copied from the user's private
        storage area to the shared area.

        """
        if not source_file:
            print('Usage: cp source_file')
            return

        if not self._assert_login():
            return

        try:
            dst_name = self._qm.copy_file(self._user, source_file)
            print('copied file "%s" to "%s"' % (source_file, dst_name))
        except Exception as e:
            print('ERROR:', e, file=sys.stderr)
            return

    complete_cp = complete_ls

    def do_rm(self, file_name):
        """Delete the specified file.

        rm file_name

        Examples:
            rm shared/some_vm.img.gz
            rm my_vm.img.gz

        Prefix the file with 'shared/' to specify removing from shared
        storage area.  Otherwise, file is removed from the user's private
        storage area.

        """
        if not file_name:
            print('Usage: rm file_name')
            return

        if not self._confirm('remove', file_name):
            return

        try:
            if self._qm.delete_file(self._user, file_name):
                print('deleted file:', file_name)
            else:
                print('file not found:', file_name)
        except Exception as e:
            print('ERROR deleting %s: %s' % (file_name, e), file=sys.stderr)
            return

    complete_rm = complete_ls

    def do_mv(self, args):
        """Rename the specified file in storage.

        mv source_file target_file

        Prefix the file with 'shared/' to specify a file in the shared storage
        area.  Otherwise, file is located in the user's private area.

        """
        if args:
            args = args.split()

        if not args or len(args) < 2:
            print('Usage: mv source_file target_file')
            return

        src = args[0]
        dst = args[1]
        if not (src.startswith('shared/') and dst.startswith('shared/')
                or self._user):
            print('login required for specifying non-shared file with mv')
            return

        try:
            new_name = self._qm.rename_file(self._user, src, dst)
            print('renamed file', src, 'to', new_name)
        except Exception as e:
            print('ERROR renaming %s: %s' % (src, e), file=sys.stderr)
            return

    complete_mv = complete_ls

    ###########################################################################
    # Server and build information methods
    #

    def do_serverinfo(self, server):
        """Get information about QManager server.

        """
        print('QManager server:', self._server)
        server_info = self._qm.get_server_info()
        for k, v in server_info.items():
            print('  %s: %s' % (k, v))

    def do_builds(self, pattern):
        """
        List available STCv builds.

        builds [build_pattern]

        Examples:
            builds
            builds 4.50.*

        """
        if not pattern:
            print('\n'.join(self._qm.get_available_stc_builds()))
            return

        for build in self._qm.get_available_stc_builds():
            if fnmatch.fnmatch(build, pattern):
                print(build)

    def complete_builds(self, text, line, begidx, endidx):
        builds = self._qm.get_available_stc_builds()
        if not text:
            return builds
        return [b for b in builds if b.startswith(text)]

    ###########################################################################
    # Start and stop VM methods
    #

    def do_startstcv(self, args):
        """Start one or more STCv VM instances on the same host.

        If an image file name is prefixed with 'shared/' this specifies to
        use that image from the shared storage area.

        Returns a list of VM ID values for started VM instances.

        OPTIONS:

        -i vm_image, --image vm_image
            Name of image file or build number.  If not specified, then use the
            latest build.  If parameter starts with '#', then a build number is
            indicated instead, and the corresponding STCv image is fetched from
            the build server.

        -t ttl_minutes, --ttl ttl_minutes
            Minutes before the VM is automatically stopped.  If not specified
            use default of one hour.

        -d vm_description, --desc vm_description
            Text describing VM instance.

        -n instances, --number instances
            Number of VM instances to start with this config.  If not specified
            then use the default of 2 instances.

        -h host_id, --host host_id
            IP or name identifying host to start VM instance on.  If not
            specified then select the best (least busy) host from hosts that
            are available to the user.

        -c core_count, --cores core_count
            Number of logical CPUs to use for each VM instance.  If not
            specified, then use 1 core.

        -m vm_mem, --memory vm_mem
            MB of memory to allocate to each VM instance.  If not specified,
            then qmanager default value (usually 512M) is used.

        --socket
            Connect VM instances with socket.  If not specified then connect
            VM instances using vbridge.

        --vlan vlan_id
            VLAN that VM instances will communicate on.  If not specified, the
            server will allocate unused VLAN from configured range.

        --ntp ntp_server
            IP address or DNS name of NTP server for STCv instance to use.  If
            not specified, use configured server.

        --license license_server
            IP address or DNS name of license server.  If not specified, use
            default license server specified in server configuration.

        --noshare
            If specifiedult), VM instances will use same different VLANs.

        --staticip ip_address
            IP address to use for VM.  If not specified, then use DHCP.

        --netmask netmask_value
            Netmask for VM.  Ignored if --staticip not given.

        --gateway gateway_ip
            Network gateway for VM.  Ignored if --staticip not given.

        """
        if not self._assert_login():
            return

        vm_image = None
        ttl_minutes = 60
        socket = False
        desc = None
        instances = 2
        host = None
        cores = 1
        memory = None
        vlan = None
        ntp_server = None
        license_server = None
        share = True
        static_ip = None
        netmask = None
        gateway = None
        external = False

        if args:
            args = args.split()
            missing_arg = 'missing value after'
            while args:
                arg = args.pop(0)
                if arg in ('-i', '--image'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    vm_image = args.pop(0)
                elif arg in ('-t', '--ttl'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    ttl_minutes = int(args.pop(0))
                elif arg in ('-d', '--desc'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    desc = args.pop(0)
                elif arg in ('-n', '--number'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    instances = int(args.pop(0))
                elif arg in ('-h', '--host'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    host = args.pop(0)
                elif arg in ('-c', '--cores'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    cores = int(args.pop(0))
                elif arg in ('-m', '--memory'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    memory = int(args.pop(0))
                elif arg == '--socket':
                    socket = True
                elif arg == '--vlan':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    vlan = int(args.pop(0))
                elif arg == '--ntp':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    ntp_server = args.pop(0)
                elif arg == '--license':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    license_server = args.pop(0)
                elif arg == '--noshare':
                    share = False
                elif arg == '--staticip':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    static_ip = args.pop(0)
                elif arg == '--netmask':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    netmask = args.pop(0)
                elif arg == '--gateway':
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    gateway = args.pop(0)
                else:
                    print('unrecognized option:', arg, file=sys.stderr)
                    return

        if not vm_image:
            builds = self._qm.get_available_stc_builds()
            if not builds:
                print('unable to find latest build', file=sys.stderr)
                return
            vm_image = '#' + builds[0]

        try:
            vm_ids = self._qm.start_stc_vm(
                self._user, vm_image, ttl_minutes, socket, desc, instances,
                host, share, vlan, memory, cores, external, ntp_server,
                license_server, static_ip, netmask, gateway)
        except Exception as e:
            print('ERROR:', e, file=sys.stderr)
            return

        print('Started new vm instances of', vm_image)
        print('\n'.join(vm_ids))


    def do_stopvm(self, args):
        """Stop the specified VM instance.

        stopvm [--vlan vlan_id] [vm_id ..]

        OPTIONS:

        --vlan vlan_id
            Stop of VM instances using this VLAN ID.

        ARGUMENTS:

        vm_id ..
            One or more VM identifiers (UUID strings) specifying VM to stop.
            If 'all' is given, then all VM instances owned by the logged in
            user are stopped.

        """
        if not self._assert_login():
            return

        vm_ids = []
        vlan = None
        if args:
            args = args.split()
            missing_arg = 'missing value after'
            while args:
                arg = args.pop(0)
                if arg in ('-v', '--vlan'):
                    if not args:
                        print(missing_arg, arg, file=sys.stderr)
                        return
                    vlan = int(args.pop(0))
                elif arg[0] == '-':
                    print('unrecognized option:', arg, file=sys.stderr)
                    return
                else:
                    vm_ids.append(arg)
                    vm_ids += args
                    break

        if vlan:
            active_vms = self._qm.get_active_vms()
            for avm in active_vms:
                if avm['owner'] == self._user:
                    vlan_id = avm.get('vlan_id')
                    if vlan_id and vlan_id == vlan:
                        vm_ids.append(avm['vm_id'])

        if not vm_ids:
            print('no VMs specified', file=sys.stderr)
            return

        stopped = []
        for vm_id in vm_ids:
            try:
                print('stopping VM:', vm_id)
                self._qm.stop_vm(self._user, vm_id)
                stopped.append(vm_id)
            except Exception, e:
                print('ERROR: failed to stop vm %s: %s' % (vm_id, e),
                      file=sys.stderr)

        print('stopped', len(vm_ids), 'VMs')


    def do_savevm(self, args):
        """Stop and save the specified VM instance.

        savevm vm_id [save_name]

        ARGUMENTS

        vm_id
            VM identifier (UUID string) specifying VM to stop.

        save_name
            Optional name to use for saving VM image.  If not specified, then
            VM ID + original VM file name is used.

         """
        if not args:
            print('missing vm id', file=sys.stderr)
            return

        args = args.split()
        vm_id = args.pop(0)
        save_name = args.pop(0) if args else None

        try:
            self._qm.stop_vm(self._user, vm_id, True, save_name)
        except Exception, e:
            print('ERROR:', e, file=sys.stderr)
            return

        print('stopped and saved vm', vm_id)


    ###########################################################################
    # Utility methods
    #

    def _assert_login(self):
        if self._user:
           return True

        print('login required before using this command', file=sys.stderr)
        return False

    def _complete_files(self, text):
        files = self._qm.list_files(self._user)
        if not text:
            return files
        return [f for f in files if f.startswith(text)]

    def _complete_hosts(self, text):
        if not text:
            return self._qm.get_available_hosts()
        return [h for h in self._qm.get_available_hosts()
                if h.startswith(text)]

    def _confirm(self, prompt, value, default=None):
        confirmed = None
        if default is None:
            default_input = None
            prompt = '%s "%s" (y/n): ' % (prompt, value)
        else:
            default = bool(default)
            default_input = 'y' if default else 'n'
            prompt = '%s "%s" (y/n) [%s]: ' % (prompt, value, default_input)

        while confirmed is None:
             yn = input(prompt).lower()
             if yn in ('y', 'yes'):
                 confirmed = True
             elif yn in ('n', 'no'):
                 confirmed = False
             else:
                 confirmed = default

        return confirmed

    def _args_to_dict(self, args):
        params = {}
        for arg in args:
            if '=' in arg:
                k, v = arg.split('=', 1)
                params[k] = v
            else:
                params[arg] = None
        return params


if __name__ == '__main__':
    server = None
    if len(sys.argv) > 1:
        server = sys.argv[1]
    else:
        server = socket.getfqdn('qmanager')

    server_ok = False
    while not server_ok:
        while not server:
            server = input('Enter QManager server: ')

        try:
            socket.gethostbyname(server)
            server_ok = True
        except socket.gaierror as e:
            print(e)
            server = None

    qmsh = QManagerCommandShell()
    readline.set_completer_delims(' \t\n;')
    qmsh._server = server
    try:
        qmsh._qm = xmlrpclib.ServerProxy('http://%s:8080' % (server,),
                                         allow_none=True)
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    qmsh.cmdloop()
