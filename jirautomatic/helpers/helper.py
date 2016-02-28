#!/usr/bin/env python

def parse_time(self, s):
    """ '1h 30m' -> 90 """
    m = 0
    for x in s.split():
        if x.endswith('d'):
            m += int(x[:-1]) * 60 * 8  # NOTE: 8, not 24
        elif x.endswith('h'):
            m += int(x[:-1]) * 60
        elif x.endswith('m'):
            m += int(x[:-1])
    return m

def to_time(self, m):
    """ 90 -> '1h 30m' """
    # d, m = divmod(m, 60 * 8)  # NOTE: 8, not 24
    h, m = divmod(m, 60)
    ret = []
    # if d:
    #     ret.append('{}d'.format(d))
    if h:
        ret.append('{}h'.format(h))
    if m:
        ret.append('{}m'.format(m))
    return ' '.join(ret) or '0m'