import warnings
import datetime
from libraries import dict_printer
from jira import JIRA
from dateutil import parser

class JiraLogger:
    def __init__(self):
        warnings.filterwarnings("ignore") # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.
        self.username = "pdelos"
        self.password = "January@2016"
        self.jira = JIRA(server="https://jira3.int.net.nokia.com/", basic_auth=(self.username, self.password));

        # self.populate_dict()
        self.__log_work_for_sprint("1603.1")

    def populate_dict(self):
        print "Fetching data from JIRA server. This will take a while..."
        issues = self.__fetch_all_issues_for_project("OMCPMNLOMG")
        issues = self.__filter_resolved_and_closed_issues(issues)

        self.__fetch_all_worklogs_for_issues(issues)
        self.__filter_worklogs_not_for_this_sprint(issues, "1602.2")
        self.__filter_worklogs_not_from_user(issues)

        pretty = dict_printer.Prettify()
        print pretty(self.__get_total_timespent_per_day_of_sprint(issues, "1602.2"))


    def __fetch_all_issues_for_project(self, project):
        return self.jira.search_issues("project={}".format(project), maxResults=False)

    # TODO: move formatting to another function
    def __filter_resolved_and_closed_issues(self, issues):
        filtered_issues = {}
        for issue in issues:
            if not (str(issue.fields.status) == "Resolved" or str(issue.fields.status) == "Closed"):
                filtered_issues[issue.id] = {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "assignee": issue.fields.assignee,
                    "reporter": issue.fields.reporter,
                    "status": issue.fields.status.name,
                    "issuetype": issue.fields.issuetype.name,
                    "subtasks": [subtask.id for subtask in issue.fields.subtasks],
                    "worklogs": [worklog.id for worklog in self.jira.worklogs(issue.id)]
                }

        return filtered_issues

    def __fetch_all_worklogs_for_issues(self, issues):
        for issue_id, issue_details in issues.items():
            worklogs_list = {}
            for worklog_id in issue_details["worklogs"]:
                worklogs_list.update(self.__fetch_worklog_details(issue_id, worklog_id))
            issue_details["worklogs"] = worklogs_list

        return issues

    # TODO: move formatting to another function
    def __fetch_worklog_details(self, issue_id, worklog_id):
        worklog = self.jira.worklog(issue_id, worklog_id)
        return {
            worklog.id: {
                "author": worklog.author,
                "date": datetime.datetime.strptime(worklog.started[:10], "%Y-%m-%d").strftime("%Y-%m-%d"),
                "timespent": worklog.timeSpent,
                "comment": worklog.comment
            }
        }

    def __filter_worklogs_not_for_this_sprint(self, issues, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details["worklogs"].items():
                if worklog_details["date"] not in dates:
                    del issue_details["worklogs"][worklog_id]

    def __filter_worklogs_not_from_user(self, issues):
        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details["worklogs"].items():
                if not worklog_details["author"].name == self.username:
                     del issue_details["worklogs"][worklog_id]

    def __get_total_timespent_per_day_of_sprint(self, issues, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])
        worklogs = {}

        for date in dates:
            worklogs[date] = []

        for issue_id, issue_details in issues.items():
            for worklog_id, worklog_details in issue_details["worklogs"].items():
                worklogs[worklog_details["date"]].append(worklog_details["timespent"])

        return {d: self.__to_time(sum(map(self.__parse_time, ts))) for d, ts in worklogs.items()}

    def __get_start_and_end_date_for_sprint(self, sprint_id):
        sprint_dates = {
            "1602.1": ["2016-01-13", "2016-01-26"],
            "1602.2": ["2016-01-27", "2016-02-16"],
            "1603.1": ["2016-02-17", "2016-03-01"]
        }.get(sprint_id, None)

        if sprint_dates is None:
            raise RuntimeError("{} is not a proper sprint id.".format(sprint_id))

        return sprint_dates

    def __generate_date_list(self, start, end):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        dates = []
        for day in range(0, (end-start).days + 1):
            date = start + datetime.timedelta(days=day)
            if date.weekday() not in [5, 6]:
                dates.append(date.strftime("%Y-%m-%d"))

        return dates

    def __parse_time(self, s):
        """ '1h 30m' -> 90 """
        m = 0
        for x in s.split():
            if x.endswith('d'):
                m += int(x[:-1]) * 60 * 8  # NOTE: 8, not 24
            elif x.endswith('h'):
                m += int(x[:-1]) * 60
            elif x.endswith('m'):
                m += int(x[:-1])
        return m

    def __to_time(self, m):
        """ 90 -> '1h 30m' """
        # d, m = divmod(m, 60 * 8)  # NOTE: 8, not 24
        h, m = divmod(m, 60)
        ret = []
        # if d:
        #     ret.append('{}d'.format(d))
        if h:
            ret.append('{}h'.format(h))
        if m:
            ret.append('{}m'.format(m))
        return ' '.join(ret) or '0m'

    def __log_work_for_sprint(self, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])

        print "Logging work"
        self.__log_daily_work(dates)

    def __log_daily_work(self, dates):
        tasks = [
            {
                "id": "OMCPMNLOMG-24",
                "timeSpent": ".75h",
                "comment": "Jira"
            },
            {
                "id": "OMCPMNLOMG-27",
                "timeSpent": ".5h",
                "comment": ""
            }
        ]

        # logging work per task
        # TODO: check if already logged. Maybe change logging per day instead.
        # TODO: check if exceeds time
        for task in tasks:
            for date in dates:
                self.jira.add_worklog(task["id"], task["timeSpent"], started=parser.parse(date + "T08:00:00-00:00"), comment=task["comment"])

    def __log_holidays_and_leaves(self):
        tasks = [
            {
                "id": "OMCPMNLOMG-24",
                "timeSpent": ".75h",
                "comment": "Jira"
            },
            {
                "id": "OMCPMNLOMG-27",
                "timeSpent": ".5h",
                "comment": ""
            }
        ]

    def __log_meeting(self):
        tasks = [
            {
                "id": "OMCPMNLOMG-23",
                "timeSpent": ".75h",
                "comment": "Jira"
            },
        ]