#!/usr/bin/env python3

import sys
import time
import lib.utils as utils
from lib.configuration import Configuration

def parse_config(args):
    """Parses the configuration file and returns a configuration object."""
    import configparser

    config = configparser.ConfigParser(allow_no_value=True)
    try:
        config.read(args.config)
    except:
        print('Could not parse configuration file "%s"' % args.config)
        raise

    if not 'Cluster' in config:
        print('Did not find a cluster section in "%s"' % args.config)
        sys.exit(1)

    if not 'machines' in config['Cluster']:
        print('The "Cluster" section must contain a list of machines')
        sys.exit(1)

    if not 'Scenario' in config:
        print('Did not find a cluster section in "%s"' % args.config)
        sys.exit(1)

    if not 'tasks' in config['Scenario']:
        print('The "Cluster" section must contain a list of machines')
        sys.exit(1)

    configuration = Configuration()

    for machine in utils.parse_wordlist(config['Cluster']['machines']):
        if not machine in config:
            print('Machine', machine, 'is not described')
            sys.exit(1)
        for k,v in config.items(machine):
            configuration.add_option(machine, k, v)

    configuration.add_forwards()

    timing = 0
    for task in utils.parse_wordlist(config['Scenario']['tasks']):
        if not task in config:
            print('Task', task, 'is not described')
            sys.exit(1)
        timing = configuration.add_task(task, config[task], timing)
    configuration.reorder_tasks()

    return configuration

def launch_task(task, conf, config):
    """Connects to the target and launches the task."""
    print('launching task', task)

    machine = config.conf[conf['target']]
    winrm = (machine.get('guest') == 'windows')
    if winrm:
        launch = launch_winrm
    else:
        launch = launch_ssh
    launch(conf['action'],
            conf['files'],
            machine.get('username', 'vagrant'),
            machine.get('password', 'vagrant'),
            config.forwards[conf['target']])

def launch_winrm(action, files, username, password, forwards):
    import winrm
    import base64

    session = winrm.Session('localhost:' + str(forwards[5985]), 
            auth=(username, password))
    try:
        for filename in files.split('\n'):
            print("Transferring file", filename)
            if filename == '':
                continue
            if '->' in filename:
                filename, destination = utils.parse_associations(filename)[0]
            else:
                destination = filename
            script = """
$filePath = "{location}"
if (Test-Path $filePath) {{
  Remove-Item $filePath
}}
            """.format(location=destination)
            cmd = session.run_ps(script)
            with open(filename, 'rb') as f:
                data = f.read(400)
                while len(data) > 0:
                    script = """
$filePath = "{location}"
$s = @"
{b64_content}
"@
$data = [System.Convert]::FromBase64String($s)
add-content -value $data -encoding byte -path $filePath
                    """.format(location=destination,
                            b64_content = base64.b64encode(data).decode('utf-8'))
                    cmd = session.run_ps(script)
                    if cmd.status_code == 1:
                        print('Could not copy file', filename)
                        print(cmd.std_err.decode('utf-8'))
                    data = f.read(400)

        for line in action.split('\n'):
            if line == '':
                continue
            cmd = session.run_ps(line)
            print('  return code:', cmd.status_code)
            print('  STDOUT:')
            print(cmd.std_out.decode('utf-8'))
            print('  STDERR:')
            print(cmd.std_err.decode('utf-8'))
    except:
        print('Winrm error running command')
        raise

def launch_ssh(action, files, username, password, forwards):
    import paramiko

    port = forwards[22]

    transport = paramiko.Transport(('localhost', port))
    try:
        transport.connect(None, username, password)
        sftp = transport.open_sftp_client()
        for filename in files.split('\n'):
            if filename == '':
                continue
            if '->' in filename:
                filename, destination = utils.parse_associations(filename)[0]
            else:
                destination = filename
            print(filename, '->', destination)
            sftp.put(filename, destination)
        transport.close()
    except:
        print('SFTP error when copying files')
        raise

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect('localhost',
                port=port,
                username=username,
                password=password,
                allow_agent=False,
                look_for_keys=False)
        for line in action.split('\n'):
            if line == '':
                continue
            stdin, stdout, stderr = client.exec_command(line)
            exit_code = stdout.channel.recv_exit_status()
            print('  return code:', exit_code)
            print('  STDOUT:')
            print(stdout.read().decode('utf-8'))
            print('  STDERR:')
            print(stderr.read().decode('utf-8'))
        client.close()
    except:
        print('SSH error running command')
        raise

def spin(args):
    """Handles the 'spin' command."""
    up(args)
    play(args)

def cut(args):
    """Handles the 'cut' command."""
    stop(args)
    halt(args)

def create(args):
    """Handles the 'create' command."""
    config = parse_config(args)
    config.write_vagrantfile(args.target)

def up(args):
    """Handles the 'up' command."""
    import subprocess
    subprocess.run(['vagrant', 'up'])

def halt(args):
    """Handles the 'halt' command."""
    import subprocess
    subprocess.run(['vagrant', 'halt'])

def play(args):
    """Handles the 'play' command."""
    from threading import Timer

    config = parse_config(args)

    tasks = []
    for task, conf in config.tasks.items():
        t = Timer(conf['timing'], launch_task, args=(task, conf, config))
        t.start()
        tasks.append(t)
    #for t in tasks:
    #    t.join()

def stop(args):
    """Handles the 'stop' command."""
    pass


if __name__ == '__main__':
    import argparse

    # Top level parser
    parser = argparse.ArgumentParser(prog='moirai')
    parser.add_argument('-c', '--config',
            help='specify a config file to use',
            default='moirai.ini',
            dest='config')
    parser.add_argument('-t', '--target',
            help='specify the target base directory for vagrant',
            default='./',
            dest='target')
    subparsers = parser.add_subparsers(title='subcommands')

    # Parser for the "spin" command
    parser_spin = subparsers.add_parser('spin',
            help='creates the Vms if necessary and plays the scenario')
    parser_spin.set_defaults(func=spin)

    # Parser for the "cut" command
    parser_cut = subparsers.add_parser('cut',
            help='stops the scenario and kills the VMs')
    parser_cut.set_defaults(func=cut)

    # Parser for the "create" command
    parser_create = subparsers.add_parser('create',
            help='create the vagrant configuration file')
    parser_create.set_defaults(func=create)

    # Parser for the "up" command
    parser_up = subparsers.add_parser('up',
            help='launches all the VMs using vagrant')
    parser_up.set_defaults(func=up)

    # Parser for the "halt" command
    parser_halt = subparsers.add_parser('halt',
            help='halts the VMs')
    parser_halt.set_defaults(func=halt)

    # Parser for the "play" command
    parser_play = subparsers.add_parser('play',
            help='plays the scenario')
    parser_play.set_defaults(func=play)

    # Parser for the "stop" command
    parser_stop = subparsers.add_parser('stop',
            help='stops the scenario')
    parser_stop.set_defaults(func=stop)

    # Parse argument and execute command
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print('No action specified')
        print(parser.format_usage(), end='')

