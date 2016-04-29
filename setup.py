#!/usr/bin/env python

import platform
import pip
import subprocess
import shlex
import sys
from jirautomatic.libraries import timer

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
            pass
            # pip.main(['install', '--upgrade', 'jira'])
            # pip.main(['install', '--upgrade', 'python-dateutil'])
        print 'Done.'
    finally:
        from jirautomatic import jira_main
        with timer.Timer():
            if platform.system() == 'Linux':
                jira_main.JiraLogger(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
            elif platform.system() == 'Windows':
                jira_main.JiraLogger(sys.argv[0], sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()