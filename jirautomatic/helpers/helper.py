#!/usr/bin/env python

def parse_time(s):
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

def to_time(m):
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

def get_holidays_list():
    non_weekend_holidays_for_2016 = {
        '2016-01-01': 'New Year\'s Day',
        '2016-02-08': 'Chinese New Year',
        '2016-02-25': 'People Power Anniversary',
        '2016-03-24': 'Maundy Thursday',
        '2016-03-25': 'Good Friday',
        '2016-08-29': 'National Heroes Day',
        '2016-10-31': 'Additional special non-working day',
        '2016-11-01': 'All Saints Day',
        '2016-11-30': 'Bonifacio Day',
        '2016-12-30': 'Rizal Day'
    }

    return non_weekend_holidays_for_2016