#!/usr/bin/env python

def generate_date_list(start, end):
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    dates = []
    for day in range(0, (end-start).days + 1):
        date = start + timedelta(days=day)
        if date.weekday() not in [5, 6] and date.strftime('%Y-%m-%d') not in get_holidays_list().keys():
            dates.append(date.strftime('%Y-%m-%d'))

    return dates

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

def get_start_and_end_date_for_sprint(sprint_id):
    sprint_dates = {
        '1602.1': ['2016-01-13', '2016-01-26'],
        '1602.2': ['2016-01-27', '2016-02-16'],
        '1603.1': ['2016-02-17', '2016-03-01'],
        '1603.2': ['2016-03-02', '2016-03-15'],
        '1604.1': ['2016-03-16', '2016-04-05'],
        '1604.2': ['2016-04-05', '2016-04-19'],
        '1605.1': ['2016-04-20', '2016-05-03'],
        '1605.2': ['2016-05-04', '2016-05-17'],
        '1606.1': ['2016-05-18', '2016-05-31']
    }.get(sprint_id, None)

    if sprint_dates is None:
        raise RuntimeError('{} is not a proper sprint id.'.format(sprint_id))

    return sprint_dates