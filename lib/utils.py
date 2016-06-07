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
            raise Exception("Invalid number of arguments in share definition")
        ret.append((a[0].strip(), a[1].strip()))
    return ret

if __name__ == '__main__':
    try:
        assert parse_wordlist('1, 2 , 3 ,,4,') == ['1', '2', '3', '4']
        print('parse_wordlist works')
    except:
        print('parse_wordlist is broken')
