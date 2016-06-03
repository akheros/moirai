#!/usr/bin/env python3

def parse_wordlist(s):
    """Transforms a string of comma separated words to a list of words."""
    return [w for w in [w.strip() for w in s.split(',')] if w != '']

if __name__ == '__main__':
    try:
        assert parse_wordlist('1, 2 , 3 ,,4,') == ['1', '2', '3', '4']
        print('parse_wordlist works')
    except:
        print('parse_wordlist is broken')
