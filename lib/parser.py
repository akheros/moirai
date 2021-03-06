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

from . import utils

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
        t = Timer(items['timing'], Task.run_task,
                args=(task, len(tasks) + 1, items, config))
        t.daemon = True
        t.start()
        tasks.append(t)

    duration = config.duration
    if duration == 0:
        for t in tasks:
            t.join()
    else:
        start = time.time()
        while time.time() < start + duration:
            finished = True
            for t in tasks:
                if not t.finished.is_set():
                    finished = False
                    break
            if finished:
                break
            time.sleep(1)

def stop(args):
    """Handles the 'stop' command."""
    pass

def create_parser():
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
            help='creates the VMs if necessary and plays the scenario')
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

    return parser
