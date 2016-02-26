#!/usr/bin/env python

import platform
import subprocess
import shlex
from jirautomatic.libraries import timer

def main():
    if platform.python_version() < "2.7":
        raise RuntimeError("Jirautomatic is only supported for Python 2.7 and higher. Please update your version now!")

    try:
        from jira import JIRA
        from dateutil import parser
    except ImportError:
        print "Installing dependecies."
        subprocess.call(shlex.split("sudo pip install jira"))
        subprocess.call(shlex.split("sudo pip install python-dateutil"))
        print "Done."
    finally:
        from jirautomatic import jira_main
        with timer.Timer():
            jira_main.JiraLogger()

if __name__ == '__main__':
    main()