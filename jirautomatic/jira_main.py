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

    def __init__(self):
        warnings.filterwarnings('ignore') # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.

        try:
            self.params = self.__get_params_from_config()
            self.jira = JIRA(server=self.params['server'], basic_auth=(self.params['username'], self.params['password']));
        except JIRAError:
            raise RuntimeError("Something went wrong in connecting to JIRA. Please be sure that your server, username and password are filled in correctly.")
        else:
            # self.__log_work_for_sprint()
            self.populate_dict()

    def populate_dict(self):
        print 'Fetching data from JIRA server. This will take a while...'
        issues = self.__fetch_all_issues_for_project()
        issues = self.__filter_resolved_and_closed_issues(issues)

        self.__fetch_all_worklogs_for_issues(issues)
        self.__filter_worklogs_not_for_this_sprint(issues)
        self.__filter_worklogs_not_from_user(issues)

        # pretty = prettify.Prettify()
        # print pretty(self.__get_total_timespent_per_day_of_sprint(issues))

    def __fetch_all_issues_for_project(self):
        return self.jira.search_issues('project={}'.format(self.params['project']), maxResults=False)

    # TODO: move formatting to another function
    def __filter_resolved_and_closed_issues(self, issues):
        filtered_issues = {}
        for issue in issues:
            if not (str(issue.fields.status) == 'Resolved' or str(issue.fields.status) == 'Closed'):
                filtered_issues[issue.id] = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'assignee': issue.fields.assignee,
                    'reporter': issue.fields.reporter,
                    'status': issue.fields.status.name,
                    'issuetype': issue.fields.issuetype.name,
                    'subtasks': [subtask.id for subtask in issue.fields.subtasks],
                    'worklogs': [worklog.id for worklog in self.jira.worklogs(issue.id)]
                }

        return filtered_issues

    def __fetch_all_worklogs_for_issues(self, issues):
        for issue_id, issue_details in issues.items():
            worklogs_list = {}
            for worklog_id in issue_details['worklogs']:
                worklogs_list.update(self.__fetch_worklog_details(issue_id, worklog_id))
            issue_details['worklogs'] = worklogs_list

        return issues

    # TODO: move formatting to another function
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

    # REMOVE: FRONTEND
    def __get_start_and_end_date_for_sprint(self):
        sprint_dates = {
            '1602.1': ['2016-01-13', '2016-01-26'],
            '1602.2': ['2016-01-27', '2016-02-16'],
            '1603.1': ['2016-02-17', '2016-03-01'],
            '1603.2': ['2016-03-02', '2016-03-15'],
            '1604.1': ['2016-03-16', '2016-04-05'],
            '1604.2': ['2016-04-05', '2016-04-19'],
            '1605.1': ['2016-04-20', '2016-05-03']
        }.get(self.params['sprint_id'], None)

        if sprint_dates is None:
            raise RuntimeError('{} is not a proper sprint id.'.format(self.params['sprint_id']))

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
        with open('sample.json') as data_file:
            try:
                data = json.load(data_file)
            except ValueError:
                raise RuntimeError("There was something wrong in you config.json. Please double check your input.")

        return data

    def __log_work_for_sprint(self):
        sprint_dates = self.__get_start_and_end_date_for_sprint()
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        # TODO: check if already logged. Maybe change logging per day instead.
        # TODO: check if exceeds time. Print warning before actually logging.

        print 'Logging work.'
        # self.__log_holidays(sprint_dates)
        # self.__log_leaves()
        self.__log_daily_work(dates)
        # self.__log_meetings()
        # self.__log_sprint_meetings(sprint_dates)
        # self.__log_trainings()
        # self.__log_reviews()
        # self.__log_other_tasks()

    def __log_holidays(self, sprint_dates):
        holidays = helper.get_holidays_list()
        print 'Logging holidays...'
        for holiday in holidays:
            if sprint_dates[0] <= holiday <= sprint_dates[1]:
                worklog = self.jira.add_worklog(self.params['holidays_id'], '8h', started=parser.parse(holiday + 'T08:00:00-00:00'), comment=holidays[holiday])
                if not isinstance(worklog, int):
                    raise RuntimeError('There was a problem logging your holidays.')

    def __log_leaves(self):
        # TODO: Support for not whole day leaves
        print 'Logging your leaves...'
        for leave in self.params['leaves']:
            worklog = self.jira.add_worklog(leave['id'], leave['timeSpent'], started=parser.parse(leave['started'] + 'T08:00:00-00:00'), comment=leave['comment'])
            print worklog
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your leaves.')

    def __log_daily_work(self, dates):
        print 'Logging your daily tasks...'
        for task in self.params['daily_tasks']:
            for date in dates:
                worklog = self.jira.add_worklog(task['id'], task['timeSpent'], started=parser.parse(date + 'T08:00:00-00:00'), comment=task['comment'])
                if not isinstance(worklog, int):
                    raise RuntimeError('There was a problem logging your daily work.')

    def __log_meetings(self):
        print 'Logging your meetings...'
        for meeting in self.params['meetings']:
            worklog = self.jira.add_worklog(meeting['id'], meeting['timeSpent'], started=parser.parse(meeting['started'] + 'T08:00:00-00:00'), comment=meeting['comment'])
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your meetings.')

    def __log_sprint_meetings(self, sprint_dates):
        print 'Logging your sprint meetings...'
        for sprint_meeting in self.params['sprint_meetings']:
            worklog = worklog = self.jira.add_worklog(sprint_meeting['id'], sprint_meeting['timeSpent'], started=parser.parse(sprint_meeting['started'] + 'T08:00:00-00:00'), comment=sprint_meeting['comment'])
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your sprint meetings.')

    def __log_trainings(self):
        print 'Logging your trainings...'
        for training in self.params['trainings']:
            worklog = self.jira.add_worklog(training['id'], training['timeSpent'], started=parser.parse(training['started'] + 'T08:00:00-00:00'), comment=training['comment'])
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your trainings.')

    def __log_reviews(self):
        # TODO: Find a way to automate this
        print 'Logging your reviews...'
        for review in self.params['reviews']:
            worklog = self.jira.add_worklog(self.params('reviews_id'), '{}h'.format(.5 * len(reviews[review])), started=parser.parse(review + 'T08:00:00-00:00'), comment='\n'.join(reviews[review]))
            if not isinstance(worklog, int):
                raise RuntimeError('There was a problem logging your reviews.')

    def __log_other_tasks(self):
        # TODO: Make this a filler task function.
        print "Not yet supported"