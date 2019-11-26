"""
# =========================================================================== #
#                                                                             #
#  Cisco ZTP Client                                  ||         ||            #
#                                                    ||         ||            #
#  Script: run.py                                   ||||       ||||           #
#                                               ..:||||||:...:||||||:..       #
#  Author: Oren Brigg                          ------------------------       #
#                                              C i s c o  S y s t e m s       #
#  Version: 0.4 beta                                                          #
#                                                                             #
# =========================================================================== #

Procedure:
1. Check if upgrade is required (version not equal to the required version).
    a. check if the file already exists on flash, if not - copy.
    b. verify the MD5 of the file.
    c. upgrade the switch.
    d. perform cleanup.
2. Clean certificates.
3. Copy the configuration file <Serial number>.cfg from the TFTP server.
4. Deploy config.

Notice the script does not perform "write mem" at the end, in case of rollback.
"""

from cli import configure, cli, pnp
import re
import json
import time

# Set Global variables to be used in later functions
tftp_server = '10.56.142.242'
img_cat3k = 'cat3k_caa-universalk9.16.09.04.SPA.bin'
img_cat3k_md5 = 'bf139ef01e88f16bf9e54c7120830eab'

img_cat9k = 'cat9k_iosxe.16.09.03s.SPA.bin'
img_cat9k_md5 = 'd454bcd2d96ce5ba6a144ff31dc3462c'
software_version = 'Cisco IOS XE Software, Version 16.09.03s'

def configure_replace(file, file_system='flash:/'):
    config_command = 'configure replace %s%s force' % (file_system, file)
    config_repl = cli(config_command)
    time.sleep(120)

def check_file_exists(file, file_system='flash:/'):
    dir_check = 'dir ' + file_system + file
    print '\n*** Checking to see if %s exists on %s ***' % (file, file_system)
    results = cli(dir_check)
    if 'No such file or directory' in results:
        print '\n*** The %s does NOT exist on %s ***' % (file, file_system)
        return False
    elif 'Directory of %s%s' % (file_system, file) in results:
        print '\n*** The %s DOES exist on %s ***' % (file, file_system)
        return True
    else:
        raise ValueError("Unexpected output from check_file_exists")

def deploy_eem_cleanup_script():
    install_command = 'install remove inactive'
    eem_commands = ['event manager applet cleanup',
                    'event none maxrun 600',
                    'action 1.0 cli command "enable"',
                    'action 2.0 cli command "%s" pattern "\[y\/n\]"' % install_command,
                    'action 2.1 cli command "y" pattern "proceed"',
                    'action 2.2 cli command "y"'
                    ]
    results = configure(eem_commands)
    print '\n*** Successfully configured cleanup EEM script on device! ***'

def deploy_eem_upgrade_script(image):
    install_command = 'install add file flash:' + image + ' activate commit'
    eem_commands = ['event manager applet upgrade',
                    'event none maxrun 600',
                    'action 1.0 cli command "enable"',
                    'action 2.0 cli command "%s" pattern "\[y\/n\/q\]"' % install_command,
                    'action 2.1 cli command "n" pattern "proceed"',
                    'action 2.2 cli command "y"'
                    ]
    results = configure(eem_commands)
    print '\n*** Successfully configured upgrade EEM script on device! ***'

def file_transfer(tftp_server, file, file_system='flash:/'):
    destination = file_system + file
    # Set commands to prepare for file transfer
    commands = ['file prompt quiet',
                'ip tftp blocksize 8192'
               ]
    results = configure(commands)
    print '\n*** Successfully set "file prompt quiet" on switch ***'
    transfer_file = "copy tftp://%s/%s %s vrf Mgmt-vrf" % (tftp_server, file, destination)
    print '\nTransferring %s to %s' % (file, file_system)
    transfer_results = cli(transfer_file)
    if 'OK' in transfer_results:
        print '\n*** %s was transferred successfully!!! ***' % (file)
    elif 'XXX Error opening XXX' in transfer_results:
        raise ValueError("XXX Failed Xfer XXX")

def find_certs():
    certs = cli('show run | include crypto pki')
    if certs:
        certs_split = certs.splitlines()
        certs_split.remove('')
        for cert in certs_split:
            command = 'no %s' % (cert)
            configure(command)

def get_serial():
    try:
        show_version = cli('show version')
    except pnp._pnp.PnPSocketError:
        time.sleep(90)
        show_version = cli('show version')
    try:
        serial = re.search(r"System Serial Number\s+:\s+(\S+)", show_version).group(1)
    except AttributeError:
        serial = re.search(r"Processor board ID\s+(\S+)", show_version).group(1)
    return serial

def upgrade_required():
    # Obtains show version output
    sh_version = cli('show version')
    # Check if switch is on approved code: 16.10.01
    # JEREMY WAS HERE
    match = sh_version.find(software_version)
    # JEREMY WAS HERE
    # Returns False if on approved version or True if upgrade is required
    if match == -1:
        return True
    else:
        return False

def verify_dst_image_md5(image, src_md5, file_system='flash:/'):
    verify_md5 = 'verify /md5 ' + file_system + image
    print '\nVerifying MD5 for ' + file_system + image
    dst_md5 = cli(verify_md5)
    if src_md5 in dst_md5:
        print '\n*** MD5 hashes match!! ***\n'
        return True
    else:
        print '\nXXX MD5 hashes DO NOT match. XXX'
        return False

def main():
    print '\n\n\n\n###### STARTING ZTP SCRIPT ######'
    print '\n*** Obtaining serial number of device.. ***'
    serial = get_serial()
    print '*** Setting configuration file variable.. ***'
    config_file = "{}.cfg".format(serial)
    print '\n*** Config file: %s ***' % config_file

    if upgrade_required():
        print '\n*** Upgrade is required. Starting upgrade process.. ***\n'
        if check_file_exists(img_cat9k):
            if not verify_dst_image_md5(img_cat9k, img_cat9k_md5):
                print '\n*** Attempting to transfer image to switch.. ***'
                file_transfer(tftp_server, img_cat9k)
                if not verify_dst_image_md5(img_cat9k, img_cat9k_md5):
                    raise ValueError('Failed Xfer')
        else:
            file_transfer(tftp_server, img_cat9k)
            if not verify_dst_image_md5(img_cat9k, img_cat9k_md5):
                raise ValueError('XXX Failed Xfer XXX')

        print '\n*** Deploying EEM upgrade script ***'
        deploy_eem_upgrade_script(img_cat9k)
        print '\n*** Performing the upgrade - switch will reboot ***\n'
        cli('event manager run upgrade')
        time.sleep(600)
    else:
        print '\n*** No upgrade is required!!! ***'

    # Cleanup any leftover install files
    print '\n*** Deploying Cleanup EEM Script ***'
    deploy_eem_cleanup_script()
    print '\n*** Running Cleanup EEM Script ***'
    cli('event manager run cleanup')
    time.sleep(30)

    if not check_file_exists(config_file):
        print '\n*** Xferring Configuration!!! ***'
        file_transfer(tftp_server, config_file)
        time.sleep(10)
    print '\n*** Removing any existing certs ***'
    find_certs()
    time.sleep(10)

    print '\n*** Deploying Configuration ***'
    try:
        configure_replace(config_file)
        configure('crypto key generate rsa modulus 4096')
    except Exception as e:
        pass
    print '\n###### FINISHED ZTP SCRIPT ######'


if __name__ in "__main__":
    main()
