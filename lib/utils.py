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

import sys

def parse_config(args, configuration):
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

    for machine in parse_wordlist(config['Cluster']['machines']):
        if not machine in config:
            print('Machine', machine, 'is not described')
            sys.exit(1)
        for k,v in config.items(machine):
            configuration.add_option(machine, k, v)

    configuration.add_forwards()

    timing = 0
    for task in parse_wordlist(config['Scenario']['tasks']):
        if not task in config:
            print('Task', task, 'is not described')
            sys.exit(1)
        timing = configuration.add_task(task, config[task], timing)
    configuration.reorder_tasks()
    configuration.add_duration(config['Scenario'].get('duration', '0'))

    return configuration

def parse_wordlist(s):
    """Transforms a string of comma separated words to a list of words."""
    return [w for w in [w.strip() for w in s.split(',')] if w != '']

def parse_associations(s):
    """Transforms string representing associations to a list of tuples."""
    lines = s.split('\n')
    ret = []
    for line in lines:
        a = line.split('->')
        if len(a) != 2:
            raise Exception("Invalid number of arguments in association")
        ret.append((a[0].strip(), a[1].strip()))
    return ret

def parse_timing(string, timing):
    """Transforms a string representing a timing to its value in seconds."""
    ret = 0
    if string.startswith('+'):
        ret += timing
        string = string[1:]
    if str.isdigit(string):
        return ret + int(string)
    tmp = 0
    last_unit = ''
    for c in string:
        if str.isdigit(c):
            tmp = 10 * tmp + int(c)
            continue
        c = c.lower()
        if (c == 'h') and (last_unit == ''):
            ret += tmp * 3600
            tmp = 0
            last_unit = c
            continue
        if (c == 'm') and (last_unit in 'h'):
            ret += tmp * 60
            tmp = 0
            last_unit = c
            continue
        if (c == 's') and (last_unit in 'hm'):
            ret += tmp
            tmp = 0
            last_unit = 's'
            continue
        raise Exception("Unknown unit or wrong unit order in timing")
    if tmp != 0:
        if last_unit == 'h':
            ret += tmp * 60
        if last_unit == 'm':
            ret += tmp
        if last_unit == 's':
            raise Exception("Unknown unit or wrong unit order in timing")
    return ret

def pretty_print(data):
    for line in data.split('\n'):
        print(' │', line)

