#!/usr/bin/env python3

from collections import OrderedDict
import lib.utils as utils

class VagrantWriter:

    def __init__(self):
        self.conf = OrderedDict()

    def add_option(self, machine, option, value):
        if not machine in self.conf:
            self.conf[machine] = {}
        self.conf[machine][option] = value

    @staticmethod
    def mount_share(machine, share, share_letter, is_windows):
        ret = ''
        if is_windows:
            ret += '    ' + machine + '.vm.provision "shell" do |s|\n'
            ret += '      s.name = "mounting share ' + share[0] + '"\n'
            ret += '      s.inline = "net use /P:Yes ' + share_letter + ': \\\\\\\\VBOXSVR\\\\' + share[1][1:] + '"\n'
            ret += '    end\n'
        return ret

    def write_config(self, target):
        with open(target + 'Vagrantfile', 'w') as f:
            f.write('# -*- mode: ruby -*-\n')
            f.write('# vi: set ft=ruby :\n\n')
            f.write('Vagrant.configure("2") do |config|\n\n')
            for machine in self.conf:
                winrm = False
                conf = self.conf[machine]
                f.write('  config.vm.define "%s" do |%s|\n'
                        % (machine, machine))
                if 'box' in conf:
                    f.write('    %s.vm.box = "%s"\n' % (machine, conf['box']))
                if 'box_url' in conf:
                    f.write('    %s.vm.box_url = "%s"\n'
                            % (machine, conf['box_url']))
                if 'guest' in conf:
                    if conf['guest'] == 'windows':
                        f.write('    %s.vm.guest = :windows\n' % machine)
                        f.write('    %s.vm.communicator = "winrm"\n' % machine)
                        winrm = True
                if 'username' in conf:
                    if winrm:
                        f.write('    %s.winrm.username = "%s"\n'
                                % (machine, conf['username']))
                    else:
                        f.write('    %s.ssh.username = "%s"\n'
                                % (machine, conf['username']))
                if 'password' in conf:
                    if winrm:
                        f.write('    %s.winrm.password = "%s"\n'
                                % (machine, conf['password']))
                    else:
                        f.write('    %s.ssh.password = "%s"\n'
                                % (machine, conf['password']))
                if 'ip' in conf:
                    if conf['ip'] == 'dhcp':
                        f.write('    %s.vm.network "private_network", type: "dhcp"\n'
                                % machine)
                    else:
                        f.write('    %s.vm.network "private_network", ip: "%s"\n'
                                % (machine, conf['ip']))
                share_letter = 'Z'
                f.write(self.mount_share(machine, ('./', '/vagrant'), share_letter, winrm))
                share_letter = chr(ord(share_letter) - 1)
                if 'shares' in conf:
                    try:
                        shares = utils.parse_associations(conf['shares'])
                        for share in shares:
                            f.write('    %s.vm.synced_folder "%s", "%s"\n'
                                    % (machine, share[0], share[1]))
                            f.write(self.mount_share(machine, share, share_letter, winrm))
                            share_letter = chr(ord(share_letter) - 1)
                    except Exception as err:
                        print('Could not parse shares. Check the syntax')
                        print('The expected syntax is one share per line')
                        print('A share is in this form: "host-folder" -> "guest-folder"')
                        print(err)
                f.write('  end\n\n')
            f.write('end\n')
            print('Vagrantfile generated in', target)

