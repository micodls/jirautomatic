#!/usr/bin/env python

import platform
import subprocess
import shlex
from jirautomatic import jira_main

def main():
    if platform.python_version() < "2.7":
        raise RuntimeError("Jirautomatic is only supported for Python 2.7 and higher. Please update your version now!")
    else:
        print "Installing dependecies."
        subprocess.call(shlex.split("sudo pip install jira"))
        print "Done."
        jira_main.JiraLogger()

if __name__ == '__main__':
    main()