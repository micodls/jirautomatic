#!/usr/bin/env python

import platform
import pip
import subprocess
import shlex

def main():
    if platform.python_version() < '2.7':
        raise RuntimeError('Jirautomatic is only supported for Python 2.7 and higher. Please update your version now!')

    # TODO: Check if pip needs upgrade
    try:
        from jira import JIRA
        from dateutil import parser
    except ImportError:
        print 'Installing dependecies.'
        if platform.system() == 'Linux':
            subprocess.call(shlex.split('sudo pip install --upgrade jira'))
            subprocess.call(shlex.split('sudo pip install --upgrade python-dateutil'))
        elif platform.system() == 'Windows':
            pip.main(['install', '--upgrade', 'jira'])
            pip.main(['install', '--upgrade', 'python-dateutil'])
    finally:
        print 'Done.'

if __name__ == '__main__':
    main()