import warnings
import datetime
from libraries import prettify
from jira import JIRA
from dateutil import parser

class JiraLogger:

    self.params = {
        username = '',
        password = '',
        server = 'https://jira3.int.net.nokia.com/',
        project = 'OMCPMNLOMG'
        sprint_id = '1603.1'
    }

    def __init__(self):
        warnings.filterwarnings('ignore') # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.
        self.jira = JIRA(server='https://jira3.int.net.nokia.com/', basic_auth=(self.username, self.password));

        # self.populate_dict()
        self.__log_work_for_sprint('1603.1')

    def populate_dict(self):
        print 'Fetching data from JIRA server. This will take a while...'
        issues = self.__fetch_all_issues_for_project('OMCPMNLOMG')
        issues = self.__filter_resolved_and_closed_issues(issues)

        self.__fetch_all_worklogs_for_issues(issues)
        self.__filter_worklogs_not_for_this_sprint(issues, '1603.1')
        self.__filter_worklogs_not_from_user(issues)

        pretty = prettify.Prettify()
        print pretty(self.__get_total_timespent_per_day_of_sprint(issues, '1603.1'))


    def __fetch_all_issues_for_project(self, project):
        return self.jira.search_issues('project={}'.format(project), maxResults=False)

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
                'date': datetime.datetime.strptime(worklog.started[:10], '%Y-%m-%d').strftime('%Y-%m-%d'),
                'timespent': worklog.timeSpent,
                'comment': worklog.comment
            }
        }

    def __filter_worklogs_not_for_this_sprint(self, issues, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
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

    def __get_total_timespent_per_day_of_sprint(self, issues, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])
        worklogs = {}

        for date in dates:
            worklogs[date] = []

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details['worklogs'].items():
                worklogs[worklog_details['date']].append(worklog_details['timespent'])

        # TODO: Rename variables
        return {d: self.__to_time(sum(map(self.__parse_time, ts))) for d, ts in worklogs.items()}

    def __get_start_and_end_date_for_sprint(self, sprint_id):
        sprint_dates = {
            '1602.1': ['2016-01-13', '2016-01-26'],
            '1602.2': ['2016-01-27', '2016-02-16'],
            '1603.1': ['2016-02-17', '2016-03-01']
        }.get(sprint_id, None)

        if sprint_dates is None:
            raise RuntimeError('{} is not a proper sprint id.'.format(sprint_id))

        return sprint_dates

    def __generate_date_list(self, start, end):
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
        dates = []
        for day in range(0, (end-start).days + 1):
            date = start + datetime.timedelta(days=day)
            if date.weekday() not in [5, 6]:
                dates.append(date.strftime('%Y-%m-%d'))

        return dates

    def __log_work_for_sprint(self, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        # TODO: check if already logged. Maybe change logging per day instead.
        # TODO: check if exceeds time. Print warning before actually logging.
        # BUG: remove holidays from date list
        # TODO: parse from config file. Properties must always be complete except for daily tasks.
        print 'Logging work.'
        # self.__log_daily_work(dates)
        # self.__log_holidays_and_leaves()
        # self.__log_meetings_and_sprint_meetings()
        # self.__log_trainings()

    def __log_daily_work(self, dates):
        tasks = [
            {
                'id': 'OMCPMNLOMG-24',
                'timeSpent': '.75h',
                'comment': 'Jira'
            },
            {
                'id': 'OMCPMNLOMG-27',
                'timeSpent': '.5h',
                'comment': ''
            }
        ]

        # logging work per task
        for task in tasks:
            for date in dates:
                self.jira.add_worklog(task['id'], task['timeSpent'], started=parser.parse(date + 'T08:00:00-00:00'), comment=task['comment'])

    def __log_holidays_and_leaves(self):
        # TODO: check if date started is in range of current sprint dates
        # TODO: generate holidays list
        holidays = [
            {
                'id': 'OMCPMNLOMG-166',
                'timeSpent': '8h',
                'started': '2016-02-25',
                'comment': 'People Power Anniversary'
            }
        ]

        leaves = [
            {
                'id': 'OMCPMNLOMG-165',
                'timeSpent': '8h',
                'started': '2016-02-23',
                'comment': 'VL'
            }
        ]

        for holiday in holidays:
            self.jira.add_worklog(holiday['id'], holiday['timeSpent'], started=parser.parse(holiday['started'] + 'T08:00:00-00:00'), comment=holiday['comment'])

        for leave in leaves:
            self.jira.add_worklog(leave['id'], leave['timeSpent'], started=parser.parse(leave['started'] + 'T08:00:00-00:00'), comment=leave['comment'])

    def __log_meetings_and_sprint_meetings(self):
        meetings = [
            {
                'id': 'OMCPMNLOMG-23',
                'timeSpent': '1h',
                'started': '2016-02-26',
                'comment': 'Cloud BTS'
            },
            {
                'id': 'OMCPMNLOMG-23',
                'timeSpent': '1h',
                'started': '2016-02-18',
                'comment': 'Dimalupig innovation meeting'
            },
            {
                'id': 'OMCPMNLOMG-23',
                'timeSpent': '1h',
                'started': '2016-02-24',
                'comment': 'CO Community'
            },
            {
                'id': 'OMCPMNLOMG-23',
                'timeSpent': '30m',
                'started': '2016-02-24',
                'comment': 'Cloud BTS'
            },
            {
                'id': 'OMCPMNLOMG-23',
                'timeSpent': '30m',
                'started': '2016-02-22',
                'comment': 'SBTS CO Community initial meeting'
            },
        ]

        # TODO: sprint planning must always be on first day
        # TODO: sprint review and retro must always be on last day
        sprint_meetings = [
            {
                'id': 'OMCPMNLOMG-20',
                'timeSpent': '1h',
                'started': '2016-02-17',
                'comment': 'Sprint Planning'
            },
            {
                'id': 'OMCPMNLOMG-20',
                'timeSpent': '2.5h',
                'started': '2016-03-01',
                'comment': 'Sprint Review + Sprint Retrospective'
            },
        ]

        for meeting in meetings:
            self.jira.add_worklog(meeting['id'], meeting['timeSpent'], started=parser.parse(meeting['started'] + 'T08:00:00-00:00'), comment=meeting['comment'])

        for sprint_meeting in sprint_meetings:
            self.jira.add_worklog(sprint_meeting['id'], sprint_meeting['timeSpent'], started=parser.parse(sprint_meeting['started'] + 'T08:00:00-00:00'), comment=sprint_meeting['comment'])

    def __log_trainings(self):
        trainings = [
            {
                'id': 'OMCPMNLOMG-152',
                'timeSpent': '2h',
                'started': '2016-02-17',
                'comment': 'Troubleshooting Domain Training Part 2'
            },
            {
                'id': 'OMCPMNLOMG-152',
                'timeSpent': '2h',
                'started': '2016-03-01',
                'comment': 'Troubleshooting Domain Training Part 3'
            },
        ]

        for training in trainings:
            self.jira.add_worklog(training['id'], training['timeSpent'], started=parser.parse(training['started'] + 'T08:00:00-00:00'), comment=training['comment'])