"""
Module to upload and download VM image file to QManager server.

There are two ways to use this module:

1) Run as script.  This will run an interactive script to upload a file from
   the command line.  Running in this mode will, by default, prompt for
   confirmation of input and print output to indicate upload progress. Example:

       python qmupload.py jdoe qemu.512-3.80.6466.img

   To see help: python qmupload.py -help


2) Import the send_file_to_qmanager function from this module into you own
   script.  See the doc string for send_file_to_qmanager for a description of
   how to call it.  Example:

       from qmupload import send_file_to_qmanager

       try:
           send_file_to_qmanager('jdoe', 'qemu.512-3.80.6466.img')
       except Exception, ex:
           print 'it did not work:', ex
       else:
           print 'upload success!'


Note: For both the command line script and the function call, the QManager
server address can be optionally specified.  By default, the Calabasas QManager
server is used.

Download:

The upload functionality works using the same parameters as download.  The
difference is that the command line requires the '-d' argument and the function
to call from a script is recv_file_from_qmanager.

When a file path is specified for download, a file with the given name is
downloaded from the qmanager to the complete file path given.  So if the given
download path is '/tmp/downloads/MyVm.img.gz', then a file named 'MyVm.img.gz'
on the server is downloaded to '/tmp/downloads/MyVm.img.gz'.

"""
from __future__ import with_statement

__author__ = "Andrew Gillis"

import socket
import os
import hashlib
import time
import sys
import xmlrpclib
import glob
import warnings
import gzip

#DEFAULT_QM_SERVER = 'qmanager.cal.ci.spirentcom.com'
DEFAULT_QM_SERVER = 'qmanager.rtp.ci.spirentcom.com'

CHUNK_SIZE = 16383
SHARED_PREFIX = 'shared/'

class ProgressBar(object):

    """
    Block-based progress bar to show amount of data that has been processed.

    """

    def __init__(self, total_size, blocks_in_bar=50, block_char='#',
                 quiet=False):
        """Initialize class instance.

        Arguments:
        total_size    -- Total amount of data that full bar represents.
        blocks_in_bar -- Characters displayed (blocks) in full bar.
        block_char    -- Character to print as a data block in bar.
        quiet         -- True to suppress output to stdout.  This can be used
                         if the caller wants to use their own display update
                         and only wants to use the output from update() and
                         finish()

        """
        assert(total_size > 1)
        assert(blocks_in_bar > 0)
        assert(isinstance(block_char, basestring))
        self._total_size = total_size
        self._total_blocks = blocks_in_bar
        self._total_done = 0
        self._blocks_printed = 0
        self._block_char = block_char
        self._quiet = quiet
        if not self._quiet:
            sys.stdout.flush()
            print '      0% [' + '-'*blocks_in_bar + '] 100%'
            print 'progress [',
            sys.stdout.flush()

    def __nonzero__(self):
        return self._total_done > 0

    def __len__(self):
        """Return size of data represented by filled portion of bar.

        Note: This can raise an overflow exception if the progress size is
        greater than sys.maxint.  If this happens, it is necessary to call the
        get_progress_size() method.

        """
        return self._total_done

    def update(self, more_size):
        """Update the progress bar with additional size completed.

        Arguments:
        more_size -- Size of additional data to represent as done (progress).

        Return:
        Number of additional blocks that get printed.

        """
        assert(more_size >= 0)
        self._total_done += more_size
        if self._total_done > self._total_size:
            self._total_done = self._total_size

        # To calculate blocks so far we do:
        #    blocks_so_far = total_sent / data_per_block
        # We know that:
        #    data_per_block = int(total_size / blocks_in_bar)
        # and that may fail when: total_size < blocks in bar, so we change
        #    blocks_so_far = total_sent / (total_size / blocks_in_bar)
        # to this:
        #    blocks_so_far = int(total_sent * blocks_in_bar / total_size)
        # which works for all cases.
        blocks_so_far = int((self._total_done * self._total_blocks) /
                            self._total_size)
        blocks_to_print = blocks_so_far - self._blocks_printed
        if not self._quiet:
            sys.stdout.write(self._block_char*blocks_to_print)
            sys.stdout.flush()
            self._blocks_printed += blocks_to_print

        return blocks_to_print

    def finish(self, show_fraction=False):
        """Show any remaining (unfinished) blocks as '.' and print end of bar.

        Arguments:
        show_fraction: If True, Print the total_done/total_size at end of bar.

        Return:
        Number of blocks less than total that were not printed.

        """
        remaining = self._total_blocks - self._blocks_printed
        if not self._quiet:
            if remaining > 0:
                sys.stdout.write('.'*remaining)
            if show_fraction:
                print '] %d/%d' %(self._total_done, self._total_size)
            else:
                print '] '
            sys.stdout.flush()

        return remaining

    def get_progress_size(self):
        """Return size of data represented by filled portion of bar.

        This is the same as calling len() on this object, except that calling
        len() will raise an exception if the progress size is greater than the
        maximum integer value for the platform.

        """
        return self._total_done

    def get_incomplete_size(self):
        """Return size of data represented by empty portion of bar."""
        return self._total_size - self._total_done

    def get_progress_percent(self):
        """Return percent of progress completion."""
        return float(self._total_done * 100 / self._total_size)

    def get_data_per_block(self):
        """Get amount of data that each block represents."""
        return self._total_size / self._total_blocks



def _make_connection(host, port, timeout):
    host = socket.gethostbyname(host)
    port = int(port)

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if timeout:
        conn.settimeout(int(timeout))

    try:
        conn.connect((host, port))
    except socket.timeout:
        raise RuntimeError('timed out trying to connect to %s:%s'
                           % (host, port))

    return conn


def _send_file(filename, host, port, print_hash=False, timeout=30):
    if not os.path.isfile(filename):
        raise Exception('%s is not a file', filename)

    conn = _make_connection(host, port, timeout)

    if print_hash:
        progress_bar = ProgressBar(os.path.getsize(filename))
    else:
        progress_bar = None

    filesize = digest = None
    try:
        with open(filename, "rb") as f:
            h = hashlib.sha1()
            while 1:
                data = f.read(CHUNK_SIZE)
                # If done reading file
                if not data:
                    break
                h.update(data)
                while len(data):
                    try:
                        sent = conn.send(data)
                        if progress_bar is not None:
                            progress_bar.update(sent)
                    except Exception, send_ex:
                        # If the socket is out of buffers, then give it a
                        # little time to send the buffered data.
                        if (str(send_ex).startswith('[Errno 35]') or
                            str(send_ex).startswith('[Errno 10035]')):
                            time.sleep(0)
                            continue
                        raise send_ex
                    if sent == len(data):
                        break
                    data = data[sent:]

            filesize = f.tell()
            digest = h.hexdigest()
    except Exception, ex:
        return False, 'Error transferring file: ' + str(ex)
    finally:
        conn.close()

    if not filesize:
        return False, 'no data transferred'

    if progress_bar is not None:
        progress_bar.finish()

    return True, {'size': filesize, 'hash': digest}


def _recv_file(dst_path, host, port, expected_size=None, timeout=30):
    conn = _make_connection(host, port, timeout)

    # Create temporary file name.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tmp_path = os.tempnam()

    if expected_size:
        progress_bar = ProgressBar(long(expected_size))
    else:
        progress_bar = None

    error = None
    filesize = digest = None
    try:
        with open(tmp_path, "wb") as f:
            h = hashlib.sha1()
            buff = bytearray(CHUNK_SIZE)
            while True:
                try:
                    recv_bytes = conn.recv_into(buff)
                except Exception as e:
                    if str(e).startswith('[Errno 35]'):
                        time.sleep(0)
                        continue
                    raise e
                if not recv_bytes:
                    break
                if progress_bar is not None:
                    progress_bar.update(recv_bytes)
                if recv_bytes < CHUNK_SIZE:
                    b = buff[:recv_bytes]
                    h.update(b)
                    f.write(b)
                else:
                    h.update(buff)
                    f.write(buff)
            f.flush()
            filesize = f.tell()
            digest = h.hexdigest()
        #print 'finished receiving file %s from %s:%s'\
        #      % (tmp_path, self._peer_addr, self._peer_port)
    except socket.timeout:
        error = 'timed out waiting for data from %s:%s' % (host, port)
    except socket.error as e:
        error = 'error reading data from %s:%s' % (host, port)
    except Exception as e:
        error = str(e)
    finally:
        conn.close()

    if not filesize:
        error = 'did not receive any data from %s:%s' % (host, port)

    if error:
        try:
            os.unlink(tmp_path)
        except:
            pass
        return False, error

    if os.path.isfile(dst_path):
        os.unlink(dst_path)

    try:
        os.rename(tmp_path, dst_path)
    except OSError:
        # Some file systems do not allow rename across different partitions.
        import shutil
        shutil.copyfile(tmp_path, dst_path)
        os.unlink(tmp_path)

    if progress_bar is not None:
        progress_bar.finish()

    return True, {'size': filesize, 'hash': digest}

def _check_file(file_path):
    """Validate that the file exists and the given extension will work with
    qmanager. Returns None or an error message if invalid."""
    if not os.path.isfile(file_path):
        return 'cannot find file: ' + file_path
    #supported_exts = ('.img', '.qcow2')
    supported_exts = ('.img', '.qcow2', '.iso')
    root, ext = os.path.splitext(file_path)

    comp_exts = ('.gz', '.bz2', '.xz')
    if ext in comp_exts:
        ext = os.path.splitext(root)[1]

    if ext not in supported_exts:
        return ('file extension %s unsupported -- must be in: %s with '
                'optional compression (%s)'
                % (ext, ', '.join(supported_exts), ', '.join(comp_exts)))

    return None

def send_file_to_qmanager(user_name, file_path, shared,
                          qmserver=DEFAULT_QM_SERVER, quiet=True):
    """Upload the specified file to the QManager server.

    The file is upload to the storage directory for the specified user.  To
    see the file in the web UI, log in as that user.  To start VM instances
    using the image file uploaded, the same user name must be specified.

    The upload works by telling the server to open a listening socket and to
    expecton a connection from the client machine.  The QManager server
    responds that it is listening and the client sends the file.

    Once the QManager server has finished receiving the file, the server
    compares its file size and sha1 hash with those values given by the client.
    If the values match, then the upload is successful.  Otherwise, the server
    deletes its version of the file and returns an error message.

    When a file is uploaded, it will not be usable or visible until the upload
    completes and the data integrity is verified.  The server keeps the file in
    a temporary location until this is done, and then moves the file into the
    user directory.

    Arguments:
    user_name -- User to upload file as.
    file_path -- Local path of file to upload.
    shared    -- True to upload file to shared storage area.  False to upload
                 file to private storage.
    qmserver  -- Optional.  QManager server DNS name or IP address.  Default
                 value is Calabasas QManager server.
    quiet     -- Optional.  Do not print output if True.

    Return:
    Nothing (None) if success.  Raises RuntimeError if error.

    """
    qms_url = 'http://%s:8080' % (qmserver,)

    file_name = os.path.basename(file_path)
    if shared:
        file_name = SHARED_PREFIX + file_name
        storage_type = 'shared'
    else:
        storage_type = 'private'

    if not quiet:
        print 'User "%s" uploading %s file "%s" to QM server %s'\
              % (user_name, storage_type, file_path, qms_url)

    qms = xmlrpclib.ServerProxy(qms_url)
    try:
        qms.get_server_time()
    except Exception as e:
        raise RuntimeError('unable to contact QManager (%s): %s' %
                           (qms_url, e))

    print_hash = False if quiet else True

    # Tell QManager to get ready to receive the file.
    #my_ip = socket.gethostbyaddr(socket.gethostname())[-1][0]
    fetch_id, server_port = qms.upload(
        user_name, file_name, str(os.path.getsize(file_path)))

    if not quiet:
        print 'sending %s file (%s) to qmanager on port %s'\
              % (storage_type, file_path, server_port)

    # Send the image file to the server.
    status, results = _send_file(file_path, qmserver, server_port, print_hash)

    # Check the results from sending the file.
    if not status:
        raise RuntimeError('failed to upload %s file: %s' %
                           (storage_type, results,))

    my_fsize = results['size']
    my_fhash = results['hash']

    result_data = None
    if not quiet:
        print 'waiting to confirm upload',
    while True:
        result_data = qms.get_transfer_results(fetch_id, my_fhash)
        if result_data:
            break
        if not quiet:
            sys.stdout.write('.')
            sys.stdout.flush()
        # Sleep, because other end may still be processing file.
        time.sleep(3)

    if not quiet:
        print

    status, qms_results = result_data
    if not status:
        raise RuntimeError('qmanager failed to get %s file: %s' %
                           (storage_type, qms_results))

    if not quiet:
        print 'successfully sent %s file (%s) to qmanager' % (
            storage_type, file_path)


def recv_file_from_qmanager(user_name, file_path, shared,
                            qmserver=DEFAULT_QM_SERVER, quiet=True):
    """Download the specified file from the QManager server.

    Arguments:
    user_name -- User to upload file as.
    file_path -- Local path of file to save.
    shared    -- True to download file from shared storage.  False to download
                 file from private storage.
    qmserver  -- Optional.  QManager server DNS name or IP address.  Default
                 value is Calabasas QManager server.
    quiet     -- Optional.  Do not print output if True.

    Return:
    Nothing (None) if success.  Raises RuntimeError if error.

    """
    qms_url = 'http://%s:8080' % (qmserver,)

    file_name = os.path.basename(file_path)
    if shared:
        file_name = SHARED_PREFIX + file_name
        storage_type = 'shared'
    else:
        storage_type = 'private'
    file_path = os.path.abspath(file_path)
    if not quiet:
        print 'User "%s" downloading %s file "%s" from QM server %s to "%s"'\
              % (user_name, storage_type, file_name, qms_url, file_path)

    qms = xmlrpclib.ServerProxy(qms_url)
    try:
        server_info = qms.get_server_info()
    except Exception, ex:
        raise RuntimeError('unable to contact QManager (%s): %s'%(qms_url,ex))

    ver = server_info.get('server_version')
    if ver < '1.0.4':
        raise RuntimeError('This version (%s) of QManager server does not '
                           'support download.' % (ver,))

    # Tell QManager to get ready to send the file.
    dl_info = qms.download(user_name, file_name)
    if not dl_info:
        raise RuntimeError('%s file not found on qmanager: %s'
                           % (storage_type, file_name))

    fetch_id = dl_info['fetch_id']
    server_port = dl_info['server_port']
    file_size = dl_info['file_size'] if not quiet else None

    if not quiet:
        print 'receiving %s file (%s) from qmanager on port %s'\
              % (storage_type, file_name, server_port)

    # Receive the file from the server.
    status, results = _recv_file(file_path, qmserver, server_port, file_size)

    # Check the results from sending the file.
    if not status:
        raise RuntimeError('failed to download %s file: %s' %
                           (storage_type, results,))

    my_fsize = results['size']
    my_fhash = results['hash']

    result_data = None
    if not quiet:
        print 'waiting to confirm download',
    while True:
        result_data = qms.transfer_results(fetch_id, my_fhash, str(my_fsize))
        if result_data:
            break
        if not quiet:
            sys.stdout.write('.')
            sys.stdout.flush()
        # Sleep, because other end may still be processing file.
        time.sleep(3)

    if not quiet:
        print

    status, qms_results = result_data
    if not status:
        try:
            os.unlink(file_path)
        except:
            pass
        raise RuntimeError('failed to get %s file from qmanager: %s' %
                           (storage_type, qms_results))

    if not quiet:
        print 'successfully received %s file from qmanager: %s' % (
            storage_type, file_path)


def is_compressed(buff):
    # Recognizer for compressed file data.
    magic = {'zip': '\x50\x4b\x03\x04',
             'gzip': '\x1f\x8b\x08',
             'bz2': '\x42\x5a\x68',
             'xz': '\xfd\x37\x7a\x58\x5a\x00'}

    for num in magic.itervalues():
        if buff.startswith(num):
            # File is recognized as compressed.
            return True

    return False


def compress(src_path):
    """If file is not already compressed, then compress it.

    If the file is already compressed, then it is not modified and the
    src_path is returned.

    Arguments:
    src_path -- Path/name of file to compress.

    Return:
    New path/name of compressed file.  This is the src_path with the
    compressed file extension (.gz) appended to it.

    """
    if src_path.endswith('.iso'):
        return src_path
    src_mtime = os.path.getmtime(src_path)
    with open(src_path, 'rb') as f_in:
        start_of_file = f_in.read(1024)
        f_in.seek(0)
        if is_compressed(start_of_file):
            return src_path

        # File is not compressed, so compress it.
        dst_path = src_path + '.gz'
        with gzip.GzipFile(dst_path, 'wb', mtime=src_mtime) as f_out:
            while True:
                data = f_in.read(CHUNK_SIZE)
                if not data:
                    break
                f_out.write(data)

    return dst_path

#
# When this module is run as a script, then interact with the user.
#
if __name__ == '__main__':

    def get_choice_number(pr, choices, default=None):
        good_range = range(1, len(choices) + 1)

        if default is not None and default in good_range:
            prompt = '%s [%s]: ' % (pr, choices[default])
        else:
            prompt = '%s: ' % (pr,)

        # Prompt and read input, coninue until valid input given.
        answer = None
        while not answer:
            for i, ch in enumerate(choices, 1):
                print '[%s] %s' % (i, ch)

            choice = raw_input(prompt)
            if choice:
                if choice.isdigit() and int(choice) in good_range:
                    answer = int(choice)
            elif default:
                answer = default
            else:
                print

        return choices[answer - 1]

    def confirm(prompt, value, default=True):
        confirmed = None
        default_input = 'y' if default else 'n'
        while confirmed is None:
             prompt = '%s "%s" (y/n) [%s]: ' % (prompt, value, default_input)
             yn = raw_input(prompt).lower()
             if yn in ('y', 'yes'):
                 confirmed = True
             elif yn in ('n', 'no'):
                 confirmed = False
             else:
                 confirmed = default

        return confirmed

    argv = list(sys.argv)
    prg = argv.pop(0)
    usage_msg = 'usage: python %s [options] user_name file_path '\
                '[qmanager_server]' % (prg,)

    ask_confirm = True
    quiet = False
    download = False
    shared = False

    while argv and argv[0].startswith('-'):
        arg = argv.pop(0)
        if arg == '-n':
            ask_confirm = False
        if arg == '-q':
            quiet = True
        if arg == '-d':
            download = True
        if arg == '-s':
            shared = True
        elif arg in ('-h', '--help', '-help', '-?'):
            print usage_msg
            print 'Options'
            print '    -d  : download a file from qmanager'
            print '    -n  : no interactive confirmation'
            print '    -q  : be quiet - do not print output'
            print '    -s  : use shared storage area'
            print
            print ('If -d specified and no file_path specified, then user '
                   'selects file from list.')
            print
            sys.exit(0)

    argc = len(argv)
    if (download and argc < 1) or (not download and argc < 2):
        print usage_msg
        print "Try 'python", prg, "--help' for more options"
        sys.exit(1)

    user_name = argv[0]
    file_path = None
    if argc >= 2:
        file_path = argv[1]
        if not download and os.path.isdir(file_path):
            file_path = glob.glob(os.path.join(file_path, '*.gz'))[0]

    file_path_ok = False
    if len(argv) >= 3:
        qmserver = argv[2]
    else:
        qmserver = DEFAULT_QM_SERVER

    if ask_confirm:
        while not confirm('Use QM server', qmserver):
            qmserver = None
            while not qmserver:
                qmserver = raw_input('QM server: ')

        op = 'Download' if download else 'Upload'
        while not confirm(op+' as user', user_name):
            user_name = None
            while not user_name:
                user_name = raw_input('Enter user name: ')

        files = []
        msg = 'Enter file path: '
        while not file_path_ok:
            if download and not file_path:
                if not files:
                    qms_url = 'http://%s:8080' % (qmserver,)
                    qms = xmlrpclib.ServerProxy(qms_url)
                    try:
                        files = qms.list_files(user_name)
                    except Exception, ex:
                        raise RuntimeError('unable to list files: %s' % (ex,))
                    if not files:
                        print 'no files available for user:', user_name
                        sys.exit(0)

                print '\nFiles available for %s:' % (user_name,)
                file_name = get_choice_number('choose file to download', files)
                file_path = os.path.join('.', file_name)

            elif not os.path.dirname(file_path):
                file_path = os.path.join('.', file_path)

            file_name = os.path.basename(file_path)
            if download:
                conf_msg = '%s file "%s" as' % (op, file_name)
            else:
                conf_msg = '%s file' % (op,)

            while not confirm(conf_msg, file_path):
                file_path = None
                while not file_path:
                    file_path = raw_input(msg)
            if download:
                dirname = os.path.dirname(file_path)
                if dirname and not os.path.isdir(dirname):
                    print 'directory', dirname, 'does not exist'
                    file_path = raw_input(msg)
                else:
                    file_path_ok = True
            else:
                errmsg = _check_file(file_path)
                if not errmsg:
                    file_path_ok = True
                else:
                    print errmsg
                    file_path = raw_input(msg)

    elif not download and _check_file(file_path):
        print _check_file(file_path)
        sys.exit(1)

    try:
        if download:
            recv_file_from_qmanager(user_name, file_path, shared, qmserver,
                                    quiet)
        else:
            comp_path = compress(file_path)
            send_file_to_qmanager(user_name, comp_path, shared, qmserver,
                                  quiet)
            if comp_path != file_path:
                os.unlink(comp_path)
    except Exception, ex:
        print 'ERROR:', ex
        sys.exit(1)
