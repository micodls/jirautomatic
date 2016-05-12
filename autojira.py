#!/usr/bin/env python

import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(__file__))
from jirautomatic.libraries import timer
from jirautomatic import jira_main

def _fetch_data_from_jira(args):
    jira = jira_main.JiraLogger(args.username, args.password)
    jira.generate_issues(args.sprint_id, args.project)

def _add_worklogs_to_jira(args):
    print args.file

class ArgsParser:
    def __init__(self):
        parser = argparse.ArgumentParser(prog='autojira')

        subparser = parser.add_subparsers()

        # fetch
        fetch_parser = subparser.add_parser('fetch', help='Fetches data from jira and returns a json file')
        fetch_parser.add_argument('username', help='Nsn-intra username')
        fetch_parser.add_argument('password', help='Nsn-intra password')
        fetch_parser.add_argument('sprint_id', help='Current sprint id')
        fetch_parser.add_argument('project', help='Jira project')
        fetch_parser.set_defaults(func=_fetch_data_from_jira)

        # log
        log_parser = subparser.add_parser('log', help='Parses a json file containing worklogs and logs the data to jira')
        log_parser.add_argument('file', help='Path to file containing jira worklogs to be logged')
        log_parser.set_defaults(func=_add_worklogs_to_jira)

        args = parser.parse_args()
        args.func(args)

def main() :
    with timer.Timer():
        ArgsParser()

if __name__ ==  '__main__':
    main()