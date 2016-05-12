import warnings
import requests
import json
import re
import os
from datetime import datetime, timedelta
from jira import JIRA
from jira.exceptions import JIRAError
from dateutil import parser
from helpers import helper

class JiraLogger:
    def __init__(self, username, password):
        warnings.filterwarnings('ignore') # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.

        self.params = self.__get_params_from_config()
        self.params['username'] = username
        self.params['password'] = password

        self.__connect_to_jira()

    def __get_params_from_config(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')) as data_file:
            try:
                data = json.load(data_file)
            except ValueError:
                raise RuntimeError("There was something wrong in your config.json.")

        return data

    def __connect_to_jira(self):
        print 'Connecting to JIRA.'
        try:
            self.jira = JIRA(server=self.params['server'], basic_auth=(self.params['username'], self.params['password']))
        except JIRAError:
            raise RuntimeError("Something went wrong in connecting to JIRA. Please be sure that your server, username and password are correct.")
        else:
            print 'Successfully connected to JIRA.'

    def generate_issues(self, sprint_id, project):
        self.params['sprint_id'] = sprint_id
        self.params['project'] = project

        sprint_dates = helper.get_start_and_end_date_for_sprint(self.params['sprint_id'])
        data = {
            "sprint_start": sprint_dates[0],
            "sprint_end": sprint_dates[1],
            "issues": self.__fetch_and_filter_data_from_jira()
        }

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'generated', '{}_{}.json'.format(self.params['username'], self.params['sprint_id'])), 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)

    def __fetch_and_filter_data_from_jira(self):
        print 'Fetching data from JIRA.'
        issues = self.__fetch_all_issues_for_project()
        issues = self.__format_issues(issues)
        self.__filter_resolved_and_closed_issues(issues)
        self.__filter_issues_not_for_current_sprint(issues)
        self.__fetch_all_worklogs_for_issues(issues)
        self.__filter_worklogs_not_for_current_sprint(issues)
        self.__filter_worklogs_not_for_current_user(issues)

        return issues

    def __fetch_all_issues_for_project(self):
        print 'Retrieving issues under {}'.format(self.params['project'])
        try:
            return self.jira.search_issues('project={}'.format(self.params['project']), maxResults=False)
        except JIRAError:
            raise RuntimeError("Project: {} is invalid or undefined.".format(self.params['project']))
        else:
            print 'Successfully retrieved issues under'.format(self.params['project'])

    def __format_issues(self, issues):
        print 'Gathering necessary information from issues.'
        formatted_issues = {}
        for issue in issues:
            formatted_issues[issue.id] = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'assignee': 'None' if issue.fields.assignee is None else issue.fields.assignee.name,
                'reporter': issue.fields.reporter.name,
                'status': issue.fields.status.name,
                'issuetype': issue.fields.issuetype.name,
                'sprint': self.__get_sprint_id(issue.fields.customfield_11990),
                'subtasks': [subtask.id for subtask in issue.fields.subtasks],
                'worklogs': {}
            }

        return formatted_issues

    def __get_sprint_id(self, sprint_details):
        if sprint_details == None:
            return 'No active sprint'

        for sprint_detail in sprint_details:
            sprint_detail = re.search('\[.*', str(sprint_detail)).group(0).split(',')
            for index, item in enumerate(sprint_detail):
                if item.startswith('state=ACTIVE'):
                     return re.search('[\d\.]+', sprint_detail[index + 1]).group(0)

        return 'No active sprint'

    def __filter_resolved_and_closed_issues(self, issues):
        print 'Removing closed and resolved issues.'
        for issue_id, issue_details in issues.items():
            if issue_details['status'] == 'Resolved' or issue_details['status'] == 'Closed':
                del issues[issue_id]

    def __filter_issues_not_for_current_sprint(self, issues):
        print 'Removing issues not for sprint {}.'.format(self.params['sprint_id'])
        for issue_id, issue_details in issues.items():
            if issue_details['sprint'] != self.params['sprint_id']:
                del issues[issue_id]

    def __fetch_all_worklogs_for_issues(self, issues):
        # if issue contains more than 20 worklogs, use curl request (~2m) since it is faster than jira-python api (~1.5hrs).
        # else, worklogs are already in issues if you use its raw version

        print 'Retrieving worklogs for issues.'

        for issue_id, issue_details in issues.items():
            try:
                raw_issue = self.jira.issue(issue_id).raw
            except JIRAError:
                raise RuntimeError("There was something wrong with retrieving issue {}.".format(issue_id))
            else:
                if raw_issue['fields']['worklog']['total'] > 20:
                    request = requests.get("{}/rest/api/latest/issue/{}/worklog".format(self.params['server'], issue_id), auth=(self.params['username'], self.params['password']))
                    if request.status_code == 200:
                        for worklog in request.json()['worklogs']:
                            issue_details['worklogs'].update(self.__format_worklog(worklog))
                    else:
                        raise RuntimeError('There was something wrong with retrieving the worklogs for {}'.format(issue_id))
                else:
                    for worklog in raw_issue['fields']['worklog']['worklogs']:
                        issue_details['worklogs'].update(self.__format_worklog(worklog))

        return issues

    def __format_worklog(self, worklog):
        return {
            worklog['id']: {
                'author': worklog['author']['name'],
                'started': worklog['started'],
                'timeSpent': worklog['timeSpent'],
                'comment': worklog['comment']
            }
        }

    def __filter_worklogs_not_for_current_sprint(self, issues):
        print 'Removing issues not for sprint {}'.format(self.params['sprint_id'])
        sprint_dates = helper.get_start_and_end_date_for_sprint(self.params['sprint_id'])
        dates = helper.generate_date_list(sprint_dates[0], sprint_dates[1])

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if re.match('\d{4}-\d{2}-\d{2}', worklog_details['started']).group(0) not in dates:
                    del issue_details['worklogs'][worklog_id]

    def __filter_worklogs_not_for_current_user(self, issues):
        print 'Removing issues not for {}'.format(self.params['username'])
        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if not worklog_details['author'] == self.params['username']:
                     del issue_details['worklogs'][worklog_id]

    def log_work(self, file):
        print 'Logging work to JIRA.'

        with open(file) as data_file:
            try:
                self.__generic_logger(json.load(data_file)['worklogs'])
            except ValueError:
                raise RuntimeError("There was something wrong in {}".format(file))

    def __generic_logger(self, worklogs):
        for worklog in worklogs:
            worklog = self.jira.add_worklog(worklog['id'], worklog['timeSpent'], started=parser.parse(worklog['started'] + 'T08:00:00-00:00'), comment=worklog['comment'])
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your worklog.')

    def test_if_add_worklog_works(self):
        print 'Testing if add_worklog works.'
        worklog = self.jira.add_worklog('OMCPMNLOMG-24', '.75h', started=parser.parse('{}T08:00:00-00:00'.format(datetime.today().strftime('%Y-%m-%d'))), comment='JIRA')
        print worklog

        while not isinstance(worklog, int):
            worklog = self.jira.add_worklog('OMCPMNLOMG-24', '.75h', started=parser.parse('{}T08:00:00-00:00'.format(datetime.today().strftime('%Y-%m-%d'))), comment='JIRA')
            print worklog