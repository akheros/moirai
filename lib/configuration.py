""" moirai
    Easily create and replay scenarios

    Copyright (C) 2016 Guillaume Brogi
    Copyright (C) 2016 Akheros

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import OrderedDict
from . import utils

class Configuration:

    def __init__(self):
        self.conf = OrderedDict()
        self.forwards = {}
        self.next_port = 2000
        self.tasks = OrderedDict()

    def add_option(self, machine, option, value):
        if not machine in self.conf:
            self.conf[machine] = {}
        self.conf[machine][option] = value

    def add_forwards(self):
        for machine, conf in self.conf.items():
            if not machine in self.forwards:
                self.forwards[machine] = {}
            is_windows = (conf.get('guest', 'linux') == 'windows')

            # Add default redirects
            if is_windows:
                self.forwards[machine][5985] = self.next_port
            else:
                self.forwards[machine][22] = self.next_port
            self.next_port += 1

            # TODO: parse additional redirects

    def add_task(self, task, conf, timing):
        try:
            timing = utils.parse_timing(conf.get('timing', '+0s'), timing)
        except Exception as err:
            print('Could not parse the timing for task', task)
            print(err)

        self.tasks[task] = {'target': conf['target'],
                'actions': conf.get('actions', ''),
                'timing': timing,
                'files': conf.get('files', ''),
                'artifacts': conf.get('artifacts', '')}
        return timing

    def reorder_tasks(self):
        self.tasks = OrderedDict(sorted(self.tasks.items(),
            key=lambda x: x[1]['timing']))

    def add_duration(self, duration):
        try:
            self.duration = utils.parse_timing(duration, 0)
        except Exception as err:
            print('Could not parse the duration of the scenario')
            print(err)

    def forward_default(self, machine, is_windows):
        ret = ''
        if is_windows:
            new_port = str(self.forwards[machine][5985])
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 22, host: 2222, id:"ssh", disabled: true\n'
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 5985, host: 55985, id:"winrm", disabled: true\n'
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 5986, host: 55986, id:"winrm-ssl", disabled: true\n'
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 5985, host: ' + new_port +'\n'
        else:
            new_port = str(self.forwards[machine][22])
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 22, host: 2222, id:"ssh", disabled: true\n'
            ret += '    ' + machine + '.vm.network :forwarded_port, guest: 22, host: ' + new_port +'\n'
        return ret

    @staticmethod
    def mount_share(machine, share, share_letter, is_windows):
        ret = ''
        if is_windows:
            ret += '    ' + machine + '.vm.provision "shell" do |s|\n'
            ret += '      s.name = "mounting share ' + share[0] + '"\n'
            ret += '      s.inline = "net use /P:Yes ' + share_letter + ': \\\\\\\\VBOXSVR\\\\' + share[1][1:] + '"\n'
            ret += '    end\n'
        return ret

    def write_vagrantfile(self, target):
        if target[-1] != '/':
            target += '/'
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
                f.write(self.forward_default(machine, winrm))
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
            print('Vagrantfile written to ' + target + 'Vagrantfile')

