#!/usr/bin/env python3

import sys
import lib.utils as utils
from lib.vagrantwriter import VagrantWriter


def create(args):
    """Handles the 'create' command."""
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

    vagrant = VagrantWriter()

    for machine in utils.parse_wordlist(config['Cluster']['machines']):
        if not machine in config:
            print('Machine', machine, 'is not described')
            sys.exit(1)
        for k,v in config.items(machine):
            vagrant.add_option(machine, k, v)
    vagrant.write_config(args.target)

def up(args):
    """Handles the 'up' command."""
    import os.path
    import subprocess

    if not os.path.isfile(args.target + 'Vagrantfile'):
        print('Generating vagrant configuration')
        create(args)
    subprocess.run(['vagrant', 'up'])



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
    subparsers = parser.add_subparsers(title='subcommands',
            help='additional help')

    # Parser for the "create" command
    parser_create = subparsers.add_parser('create',
            help='create the vagrant configuration file')
    parser_create.set_defaults(func=create)

    # Parser for the "up" command
    parser_up = subparsers.add_parser('up',
            help='launches all the VMs using vagrant and creates the vagrant configuration if it doesn\'t exist')
    parser_up.set_defaults(func=up)

    # Parse argument and execute command
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print('No action specified')
        print(parser.format_usage(), end='')

