#!/usr/bin/env python3

import sys
import time
import lib.utils as utils


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
    from lib.configuration import Configuration

    config = utils.parse_config(args, Configuration())
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
    from lib.configuration import Configuration
    from lib.task import Task

    config = utils.parse_config(args, Configuration())

    tasks = []
    for task, items in config.tasks.items():
        t = Timer(items['timing'], Task.run_task, args=(task, items, config))
        t.start()
        tasks.append(t)
    for t in tasks:
        t.join()

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

