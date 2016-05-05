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

    def __init__(self, username, password, sprint_id, project):
        warnings.filterwarnings('ignore') # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.

        self.username = username
        self.password = password
        self.sprint_id = sprint_id
        self.project = project

        try:
            self.params = self.__get_params_from_config()
            self.jira = JIRA(server=self.params['server'], basic_auth=(self.username, self.password))
        except JIRAError:
            raise RuntimeError("Something went wrong in connecting to JIRA. Please be sure that your server, username and password are correct.")
        else:
            # self.__test_if_add_worklog_works()
            self.create_input_json()

    def create_input_json(self):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        data = {
            "sprint_start": sprint_dates[0],
            "sprint_end": sprint_dates[1],
            "issues": self.__fetch_and_filter_data_from_jira()
        }

        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), '{}_{}.json'.format(self.username, self.sprint_id)), 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)

    def __fetch_and_filter_data_from_jira(self):
        print 'Fetching data from JIRA server. This will take a while...'
        issues = self.__fetch_all_issues_for_project()
        issues = self.__filter_resolved_and_closed_issues(issues)
        self.__filter_issues_not_for_current_sprint(issues)
        self.__fetch_all_worklogs_for_issues(issues)
        self.__filter_worklogs_not_for_current_sprint(issues)
        self.__filter_worklogs_not_for_current_user(issues)

        return issues

    def __fetch_all_issues_for_project(self):
        try:
            return self.jira.search_issues('project={}'.format(self.project), maxResults=False)
        except JIRAError:
            raise RuntimeError("Project is invalid or undefined.")

    def __filter_resolved_and_closed_issues(self, issues):
        filtered_issues = {}
        for issue in issues:
            if not (str(issue.fields.status) == 'Resolved' or str(issue.fields.status) == 'Closed'):
                filtered_issues[issue.id] = {
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

        return filtered_issues

    def __filter_issues_not_for_current_sprint(self, issues):
        for issue_id, issue_details in issues.items():
            if issue_details['sprint'] != self.sprint_id:
                del issues[issue_id]

    def __fetch_all_worklogs_for_issues(self, issues):
        for issue_id, issue_details in issues.items():
            raw_issue = self.jira.issue(issue_id).raw
            if raw_issue['fields']['worklog']['total'] > 20:
                r = requests.get("{}/rest/api/latest/issue/{}/worklog".format(self.params['server'], issue_id), auth=(self.username, self.password))
                if r.status_code == 200:
                    for worklog in r.json()['worklogs']:
                        issue_details['worklogs'].update({
                            worklog['id']: {
                                'author': worklog['author']['name'],
                                'started': worklog['started'],
                                'timeSpent': worklog['timeSpent'],
                                'comment': worklog['comment']
                            }
                        })
                else:
                    raise RuntimeError('There was something wrong with getting the worklogs for {}'.format(issue_id))
            else:
                for worklog in raw_issue['fields']['worklog']['worklogs']:
                    issue_details['worklogs'].update({
                        worklog['id']: {
                            'author': worklog['author']['name'],
                            'started': worklog['started'],
                            'timeSpent': worklog['timeSpent'],
                            'comment': worklog['comment']
                        }
                    })

        return issues

    def __filter_worklogs_not_for_current_sprint(self, issues):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if re.match('\d{4}-\d{2}-\d{2}', worklog_details['started']).group(0) not in dates:
                    del issue_details['worklogs'][worklog_id]

    def __filter_worklogs_not_for_current_user(self, issues):
        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if not worklog_details['author'] == self.username:
                     del issue_details['worklogs'][worklog_id]

    def __get_start_and_end_date_for_sprint(self):
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
        }.get(self.sprint_id, None)

        if sprint_dates is None:
            raise RuntimeError('{} is not a proper sprint id.'.format(self.sprint_id))

        return sprint_dates

    def __generate_date_list(self, start, end):
        start = datetime.strptime(start, '%Y-%m-%d')
        end = datetime.strptime(end, '%Y-%m-%d')
        dates = []
        for day in range(0, (end-start).days + 1):
            date = start + timedelta(days=day)
            if date.weekday() not in [5, 6] and date.strftime('%Y-%m-%d') not in helper.get_holidays_list().keys():
                dates.append(date.strftime('%Y-%m-%d'))

        return dates

    def __get_params_from_config(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')) as data_file:
            try:
                data = json.load(data_file)
            except ValueError:
                raise RuntimeError("There was something wrong in your config.json.")

        return data

    def __get_sprint_id(self, sprint_details):
        if sprint_details == None:
            return 'No active sprint'

        for sprint_detail in sprint_details:
            sprint_detail = re.search('\[.*', str(sprint_detail)).group(0).split(',')
            for index, item in enumerate(sprint_detail):
                if item.startswith('state=ACTIVE'):
                     return re.search('[\d\.]+', sprint_detail[index + 1]).group(0)

        return 'No active sprint'

    def log_work_for_sprint(self, file):
        print 'Logging work.'

        with open(file) as data_file:
            try:
                self.__generic_logger(json.load(data_file))
            except ValueError:
                raise RuntimeError("There was something wrong in your {}.json." + file)

    def __generic_logger(self, worklogs):
        for worklog in worklogs:
            worklog = self.jira.add_worklog(worklog['id'], worklog['timeSpent'], started=parser.parse(worklog['started'] + 'T08:00:00-00:00'), comment=worklog['comment'])
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your holidays.')

    def __test_if_add_worklog_works(self):
        worklog = self.jira.add_worklog('OMCPMNLOMG-24', '.75h', started=parser.parse('2016-04-26T08:00:00-00:00'), comment='JIRA')
        print worklog

        while not isinstance(worklog, int):
            worklog = self.jira.add_worklog('OMCPMNLOMG-24', '.75h', started=parser.parse('2016-05-03T08:00:00-00:00'), comment='JIRA')
            print worklog