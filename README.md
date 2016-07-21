# moirai -- Easily create and replay scenarios

moirai has been developed to make it easy to create, replay and share scenarios. 
These scenarios are, for example, used to test security solutions and involve 
multiple machines.

The community can share scenarios [here](/akheros/moirai-scenarios).


## State

This is still a very early version. Capabilities are added when they are 
required. This is a short list of things that should be added. It is neither 
exhaustive nor definite. Requests are welcome.

- [ ] Check windows' version and adjust behaviour
- [ ] Add capability to redirect arbitrary IPs and hostnames
- [ ] Mount shares in linux
- [ ] Add option to display GUI
- [ ] Retrieve artifacts if tasks are killed by global timeout


## Dependencies

moirai uses `vagrant` to manage virtual machines. It connects to these machines 
using either `ssh` or `WinRM`.

The necessary packages are:
- vagrant
- virtualbox
- python 3
- paramiko
- pywinrm


## Quickstart

1. Write a `moirai.ini` file describing your scenario:
    ```ini
    [Cluster]
    machines = winxp, archlinux

    [winxp]
    box = IE8.XP.For.Vagrant
    guest = windows
    username = IEUser
    password = Passw0rd!
    ip = 192.168.51.5
    shares = /tmp -> /host_tmp

    [archlinux]
    box = terrywang/archlinux
    shares = /tmp -> /host_tmp

    [Scenario]
    tasks = check_disks, list_files, sleep
    duration = 1m

    [check_disks]
    target = winxp
    timing = 10s
    actions = wmic logicaldisk get caption > disks.txt
    artifacts = disks.txt

    [list_files]
    target = archlinux
    timing = +10s
    actions = ls -lah > file_list
    files = .bashrc
            .bash_history -> history
    artifacts = file_list -> archlinux_ls

    [sleep]
    target = archlinux
    timing = +20s
    actions = sleep 120
    ```
   The `[Cluster]` section gives the name of each machine. Each machine is then 
   described in its own section. Then the `[Scenario]` section lists the name of 
   each task. The tasks are then described in their own sections. For more 
   information on how each option works, check the [wiki](../../wiki).
2. Use `moirai create` to generate a `Vagrantfile`. Check to see if you want to 
   add anything.
3. `moirai up` launches the VMs and sets them up.
4. `moirai play` plays the scenario


## Why moirai?

The Moirai are the greek equivalent of the Parcæ, who spun the web of life. It 
seemed fitting that they spun the web of life of these VMs. And it fits with 
Akheros, one of the rivers sailed by Charon.
