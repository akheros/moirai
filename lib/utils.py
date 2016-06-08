#!/usr/bin/env python3

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

if __name__ == '__main__':
    try:
        assert parse_wordlist('1, 2 , 3 ,,4,') == ['1', '2', '3', '4']
        print('parse_wordlist works')
    except:
        print('parse_wordlist is broken')
