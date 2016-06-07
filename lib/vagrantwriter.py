#!/usr/bin/env python3

from collections import OrderedDict

class VagrantWriter:

    def __init__(self):
        self.conf = OrderedDict()

    def add_option(self, machine, option, value):
        if not machine in self.conf:
            self.conf[machine] = {}
        self.conf[machine][option] = value

    def write_config(self, target):
        with open(target + 'Vagrantfile', 'w') as f:
            f.write('# -*- mode: ruby -*-\n')
            f.write('# vi: set ft=ruby :\n\n')
            f.write('Vagrant.configure("2") do |config|\n\n')
            for machine in self.conf:
                conf = self.conf[machine]
                f.write('  config.vm.define "%s" do |%s|\n'
                        % (machine, machine))
                if 'box' in conf:
                    f.write('    %s.vm.box = "%s"\n' % (machine, conf['box']))
                if 'box_url' in conf:
                    f.write('    %s.vm.box_url = "%s"\n'
                            % (machine, conf['box_url']))
                if 'guest' in conf:
                    winrm = False
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
                        f.write('    %s.vm.network "private_network", ip: "%s"'
                                % (machine, conf['ip']))
                f.write('  end\n\n')
            f.write('end\n')
            print('Vagrantfile generated in', target)

