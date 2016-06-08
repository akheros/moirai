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

def launch_task(task, conf):
    print('launching task', task, 'with conf', conf)

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
        t = Timer(conf['timing'], launch_task, args=(task, conf))
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

