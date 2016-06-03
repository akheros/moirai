#!/usr/bin/env python3

from collections import OrderedDict

class VagrantWriter:
#config.vm.box

#config.vm.box_url -> file://

#config.vm.communicator -> ssh|winrm
#config.vm.guest -> :linux|:windows
#config.vm.network
#config.vm.provision
#config.vm.synced_folder

    prefix = """Vagrant.configure("2") do |config|"""
    postfix = """end"""
    machine_prefix = """  config.vm.define "%s" do |%s|"""
    machine_postfix = """  end"""

    def format_config(vmname, option, value):
        return '%s.vm.%s = %s' % (vname, option, value)

    def __init__(self):
        self.conf = OrderedDict()

    def add_option(self, machine, option, value):
        if not machine in self.conf:
            self.conf[machine] = {}
        self.conf[machine][option] = value

    def write_config(self, target):
        with open(target + 'Vagrantfile', 'w') as f:
            f.write('Vagrant.configure("2") do |config|\n')
            for machine in self.conf:
                conf = self.conf[machine]
                f.write('  config.vm.define "%s" do |%s|\n'
                        % (machine, machine))
                if 'box' in conf:
                    f.write('    %s.vm.box = "%s"\n' % (machine, conf['box']))
                if 'box_url' in conf:
                    f.write('    %s.vm.box_url = "file://%s"\n'
                            % (machine, conf['box_url']))
                if 'guest' in conf:
                    if conf['guest'] == 'windows':
                        f.write('    %s.vm.communicator = "winrm"\n' % machine)
                        f.write('    %s.vm.guest = :windows\n' % machine)
                if 'network' in conf:
                    pass
                if 'provision' in conf:
                    pass
                if 'synced_folder' in conf:
                    pass
                f.write('  end\n')
            f.write('end\n')
            print('Vagrantfile generated in', target)

