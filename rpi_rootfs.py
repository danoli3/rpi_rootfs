#!/usr/bin/env python
#
#
#

import os
import subprocess
import sys
import re
import errno

## Syncing Directory/File Pattern
rsync_include = ['etc/', 'lib/','usr/','opt/vc']

## Rsync Options
rsync_cmd = ['/usr/bin/rsync']
#rsync_options = ['-rRlvu', '--stats',  '--delete-after', '--include=etc/ld.so.*', \
#        '--include=usr/share/pkg*' ]
rsync_options = ['-rRlvu', '--stats',  '--delete-after' ]

EXCLUDE_PATH_PATTERN = r'^/proc/|^/dev/'

################################################################################
#
# Rsync
#
################################################################################
## Error code from rsync manual page
def rsync_err_msg(retcode):
    errorcode_to_msg  = {
        1: "Syntax or usage error",
        2: "Protocol incompatibility",
        3: "Errors selecting input/output files, dirs",
        4: "Requested  action not supported: an attempt was made to manipulate 64-bit files on a platform\
that cannot support them; or an option was specified that is supported by the client and  not\
by the server.",
        5: "Error starting client-server protocol",
        6: "Daemon unable to append to log-file",
        10: "Error in socket I/O",
        11: "Error in file I/O",
        12: "Error in rsync protocol data stream",
        13: "Errors with program diagnostics",
        14: "Error in IPC code",
        20: "Received SIGUSR1 or SIGINT",
        21: "Some error returned by waitpid()",
        22: "Error allocating core memory buffers",
        23: "Partial transfer due to error",
        24: "Partial transfer due to vanished source files",
        25: "The --max-delete limit stopped deletions",
        30: "Timeout in data send/receive",
        35: "Timeout waiting for daemon connection"
    }
    return errorcode_to_msg.get(retcode, "error code not found")

#
def rsync_get_include_option(user):
    return ''.join([user] + [':/'] + rsync_include)

#
def process_rsync_rootfs(user, path):
    # Building rsync command line
    rsync_full_command = rsync_cmd + rsync_options + [
        f"--include={' '.join(rsync_include)}",
        "--exclude='*'",
        f"{user}:/",
        path
    ]
    # rsync_full_command = rsync_cmd + rsync_options  + \
    #         ["--include-from=data/rsync_include_list.txt"] + \
    #         ["--exclude-from=data/rsync_exclude_list.txt"] + \
    #         [rsync_get_include_option(user)] + [path]
    print(rsync_full_command)
    ret = subprocess.call(rsync_full_command, shell=False)
    if ret != 0:
        print("Rsync error : %s" % rsync_err_msg( ret) )
    return ret


################################################################################
#
# Convert absolute link to relative link
#   : This content copied from sysroot-relativelinks.py in YoctoProejct
#
################################################################################
## 

def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}\n{e.stderr}")
        return None

def relativelinks_handlelink(topdir, filep, subdir):
    link = os.readlink(filep)
    if not link.startswith('/'):
        return
    if link.startswith(topdir):
        return
    target_path = os.path.join(topdir, link.lstrip('/'))
    if os.path.exists(target_path):
        rel_path = os.path.relpath(target_path, subdir)
        os.unlink(filep)
        os.symlink(rel_path, filep)
    
    if link.startswith('/'):
        print("File Starting %s link %s" % (filep,link))

    #print("Replacing %s with %s for %s" % (link, os.path.relpath(topdir+link, subdir), filep))


def process_relativelinks(path):
    topdir = os.path.abspath(path)

    for subdir, dirs, files in os.walk(topdir):
        if any(re.findall(EXCLUDE_PATH_PATTERN, subdir, re.IGNORECASE)):
            continue
        for f in files:
            filep = os.path.join(subdir, f)
            if os.path.islink(filep):
                #print("Considering %s, Subdir: %s" % (filep, subdir))
                relativelinks_handlelink(topdir, filep, subdir) 


################################################################################
#
# making pkg-config links
#
################################################################################

def symlink_force(target, link_name):
    """
    Create a symbolic link at 'link_name' pointing to 'target'. If a file or
    symlink already exists at 'link_name', it is replaced.
    """
    try:
        # Check if the target exists
        if not os.path.exists(target):
            raise FileNotFoundError(f"Target '{target}' does not exist.")
        
        # If the link_name already exists, remove it
        if os.path.lexists(link_name):  # lexists checks even broken symlinks
            try:
                os.remove(link_name)
            except IsADirectoryError:
                # If it's a directory, use rmdir instead
                os.rmdir(link_name)
        
        # Create the symbolic link
        os.symlink(target, link_name)
        print(f"Symlink created: {link_name} -> {target}")
    
    except OSError as e:
        # Handle specific errors
        if e.errno == errno.EEXIST:
            print(f"Error: Path '{link_name}' exists and could not be removed.")
        elif e.errno == errno.EACCES:
            print(f"Error: Permission denied while accessing '{link_name}' or '{target}'.")
        else:
            print(f"Unexpected error ({e.errno}): {e}")

def process_pkgconfig_link(path):
    # 
    pkgconfig_path  = os.path.abspath(path)+'/usr/lib/arm-linux-gnueabihf/pkgconfig'
    if(os.path.exists(pkgconfig_path)):
        print("pkg config: %s" % pkgconfig_path)
        for subdir, dirs, files in os.walk(pkgconfig_path):
            for f in files:
                filep = os.path.join(subdir, f)
                target_packageconfig = "../../lib/arm-linux-gnueabihf/pkgconfig/" + f
                link_packageconfig =  os.path.abspath(path) + "/usr/share/pkgconfig/" + f
                print("source %s target %s" % (target_packageconfig, link_packageconfig))
                symlink_force(target_packageconfig, link_packageconfig)
                
    else:
        sys.stderr.write('ERROR: pkg-config does not exist : %r\n\n' % pkgconfig_path)

################################################################################
#
# GNU linker script fixing
# This function will search the entire rootfs path with 'grep' command.
#
################################################################################
def inplace_change(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    try:
        # Safely write the changed content, if found in the file
        with open(filename, 'w') as f:
            print ('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
            s = s.replace(old_string, new_string)
            f.write(s)
    except OSError, e:
        print("Error: %s -- target:\"%s\"" % (e, filename) )
        return
    # TODO: need to handle permission error 
    except IOError, e:
        print("Error: %s -- target:\"%s\"" % (e, filename) )
        return


def fix_process_ld_scripts(path, filename):
    file_contents = [] 
    if not os.path.exists(filename):
        print("linker script file does not exist: %s" % filename )

    with open(filename) as fstream:
        file_contents = fstream.readlines()


    #
    # Check whether this file is GNU linker script
    if not '/* GNU ld script' in file_contents[0]:
        # stop fixing link script
        print("file is not linker script: %s" % filename )
        return

    #
    # Search 'GROUP' keyword in file content
    for index, line_content in enumerate( file_contents ):
        if 'GROUP' in line_content:
            token_list = [x for x in re.split('[(), ]', line_content) if x]
            for index, item in enumerate(token_list):
                if os.path.exists(path + item):
                    if item[0] == "/":
                        # This means that this item have absolute path, it need to be fixed
                        split_head, split_tail = os.path.split(filename)
                        relpath = os.path.relpath(path+item, split_head)
                        inplace_change(filename, item, relpath)


process_ld_scripts_command = [
    '/usr/bin/grep', '-rl',
    '--include=*.so', '--exclude=*',
    '\"GNU ld script\"', '{}'
]
def process_ld_scripts(path):
    grep_command = ' '.join(process_ld_scripts_command).format(path)
    proc = subprocess.Popen(grep_command,stdout=subprocess.PIPE, shell=True)
    for line in proc.stdout:
        #the real code does filtering here
        fix_process_ld_scripts(path, line.strip())

################################################################################
#
# ld.so.preload fixing
#
################################################################################
process_ld_so_preload_command = [ '/usr/bin/grep', '-rl', '--exclude=*', 
        '--include=*.preload', '{}', '{}' ]
def process_ld_so_preload(path):
    grep_command = ' '.join(process_ld_so_preload_command).format('{PLATFORM}',path)
    proc = subprocess.Popen(grep_command,stdout=subprocess.PIPE, shell=True)
    for line in proc.stdout:
        # replacing to 'v7l'
        inplace_change(line.strip(), '${PLATFORM}', 'v7l')

################################################################################
#
# Main Function
#
################################################################################
def main(argv):
    if len(argv) != 3:
        sys.stderr.write(
                'Usage: ' + argv[0] + ' [<user@hostname>|local] <rootfs path>\n')
        sys.stderr.write(
                '\tuser@hostname : Rpi host address and user information for rcp connection\n')
        sys.stderr.write(
                '\tlocal : Performs fixing processes without image copying.\n')
        return 1

    if not sys.platform.startswith('linux'):
        sys.stderr.write('RPi RootFS does not support this platform: %r\n\n' % sys.platform)
        return 1

    sync_image_url = argv[1]
    rootfs_path = argv[2];

    if sync_image_url != 'local':
        print("################################################################################")
        print("###\n### rootfs syncing from %s\n###" % argv[1] )
        print("################################################################################")
        ret = process_rsync_rootfs(sync_image_url, rootfs_path)
        if ret != 0:
            ## Failed to rsync the remote file system, aborting!
            return ret

    print("################################################################################")
    print("###\n### fixing absolute links\n###" )
    print("################################################################################")
    process_relativelinks(rootfs_path);

    print("################################################################################")
    print("###\n### linking pkgconfig on /usr/share/pkginfo \n###" )
    print("################################################################################")
    process_pkgconfig_link(rootfs_path);

    print("################################################################################")
    print("###\n### fixing ld scripts absolute path to relative path \n###" )
    print("################################################################################")
    process_ld_scripts(rootfs_path);

    print("################################################################################")
    print("###\n### fixing ld.so.preload \n###" )
    print("################################################################################")
    process_ld_so_preload(rootfs_path);

if __name__ == '__main__':
    sys.exit(main(sys.argv))


