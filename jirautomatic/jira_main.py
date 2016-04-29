import warnings
import json
import re
from datetime import datetime, timedelta
from jira import JIRA
from jira.exceptions import JIRAError
from dateutil import parser
from libraries import prettify
from helpers import helper

class JiraLogger:

    def __init__(self, username, password, sprint_id, project):
        warnings.filterwarnings('ignore') # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.

        self.username = username
        self.sprint_id = sprint_id
        self.project = project

        try:
            self.params = self.__get_params_from_config()
            self.jira = JIRA(server=self.params['server'], basic_auth=(self.username, password))
        except JIRAError:
            raise RuntimeError("Something went wrong in connecting to JIRA. Please be sure that your server, username and password are correct.")
        else:
            self.create_input_json()

    def create_input_json(self):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        data = {
            "sprint_start": sprint_dates[0],
            "sprint_end": sprint_dates[1],
            "issues": self.__fetch_and_filter_data_from_jira()
        }

        with open('{}_{}.json'.format(self.username, self.sprint_id), 'w') as outfile:
            json.dump(data, outfile)

    def __fetch_and_filter_data_from_jira(self):
        print 'Fetching data from JIRA server. This will take a while...'
        issues = self.__fetch_all_issues_for_project()
        issues = self.__filter_resolved_and_closed_issues(issues)
        self.__filter_issues_not_for_sprint(issues)
        # self.__fetch_all_worklogs_for_issues(issues)
        # self.__filter_worklogs_not_for_this_sprint(issues)
        # self.__filter_worklogs_not_from_user(issues)
        # pretty = prettify.Prettify()
        # print pretty(self.__get_total_timespent_per_day_of_sprint(issues))

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
                    'subtasks': [subtask.id for subtask in issue.fields.subtasks]
                    # 'worklogs': [worklog.id for worklog in self.jira.worklogs(issue.id)]
                }

        return filtered_issues

    def __filter_issues_not_for_sprint(self, issues):
        for issue_id, issue_details in issues.items():
            if issue_details['sprint'] != self.sprint_id:
                del issues[issue_id]

    def __fetch_all_worklogs_for_issues(self, issues):
        for issue_id, issue_details in issues.items():
            worklogs_list = {}
            for worklog_id in issue_details['worklogs']:
                worklogs_list.update(self.__fetch_worklog_details(issue_id, worklog_id))
            issue_details['worklogs'] = worklogs_list

        return issues

    def __fetch_worklog_details(self, issue_id, worklog_id):
        worklog = self.jira.worklog(issue_id, worklog_id)
        return {
            worklog.id: {
                'author': worklog.author,
                'date': datetime.strptime(worklog.started[:10], '%Y-%m-%d').strftime('%Y-%m-%d'),
                'timespent': worklog.timeSpent,
                'comment': worklog.comment
            }
        }

    def __filter_worklogs_not_for_this_sprint(self, issues):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if worklog_details['date'] not in dates:
                    del issue_details['worklogs'][worklog_id]

    def __filter_worklogs_not_from_user(self, issues):
        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                if not worklog_details['author'].name == self.username:
                     del issue_details['worklogs'][worklog_id]

    def __get_total_timespent_per_day_of_sprint(self, issues):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])
        worklogs = {}

        for date in dates:
            worklogs[date] = []

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                worklogs[worklog_details['date']].append(worklog_details['timespent'])

        return {date: helper.to_time(sum(map(helper.parse_time, timespent))) for date, timespent in worklogs.items()}

    def __get_start_and_end_date_for_sprint(self):
        sprint_dates = {
            '1602.1': ['2016-01-13', '2016-01-26'],
            '1602.2': ['2016-01-27', '2016-02-16'],
            '1603.1': ['2016-02-17', '2016-03-01'],
            '1603.2': ['2016-03-02', '2016-03-15'],
            '1604.1': ['2016-03-16', '2016-04-05'],
            '1604.2': ['2016-04-05', '2016-04-19'],
            '1605.1': ['2016-04-20', '2016-05-03']
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
        with open('config.json') as data_file:
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