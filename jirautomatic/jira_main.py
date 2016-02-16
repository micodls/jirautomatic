import warnings
import datetime
from jira import JIRA

class JiraLogger:
    def __init__(self):
        warnings.filterwarnings("ignore") # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.
        self.jira = JIRA(server="http://jira3.int.net.nokia.com", basic_auth=("pdelos", "January@2016"));

        # print self.show_worklog_for_issue("OMCPMNLOMG-29")
        # self.display_worklogs_for_sprint("1602.2")
        self.populate_dict()

    def populate_dict(self):
        print "Fetching data from JIRA server. This may take a while..."
        issues = self.fetch_all_issues_for_project("OMCPMNLOMG")
        issues = self.__filter_resolved_and_closed_issues(issues)
        issues = self.__fetch_all_worklogs_for_issues(issues)
        pretty = Formatter()
        print(pretty(issues))

    def fetch_all_issues_for_project(self, project):
        return self.jira.search_issues("project={}".format(project), maxResults=False)

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

    def __fetch_worklog_details(self, issue_id, worklog_id):
        worklog = self.jira.worklog(issue_id, worklog_id)
        return {
            worklog.id: {
                "author": worklog.author,
                "date": worklog.started,
                "timespent": worklog.timeSpent,
                "comment": worklog.comment
            }
        }

    def __fetch_all_worklogs_for_issues(self, issues):
        for id, details in issues.items():
            for worklog in details["worklogs"]:
                worklog = self.__fetch_worklog_details(id, worklog)

        return issues

    def __display_issue(self, issue, tabbing=0):
        tab = "\t" * tabbing
        print "{}Id: {}".format(tab, issue.key)
        print "{}Summary: {}".format(tab, issue.fields.summary)
        print "{}Assignee: {}".format(tab, issue.fields.assignee)
        print "{}Reporter: {}".format(tab, issue.fields.reporter)
        print "{}Status: {}".format(tab, issue.fields.status)
        print "--------------------------------------------"

    def get_all_issue_of_issuetype(self, project, issuetype):
        for issue in self.fetch_all_issues_for_project(project):
            if (str(issue.fields.status) == "In Progress" or str(issue.fields.status) == "Reopened" or str(issue.fields.status) == "Open") and str(issue.fields.issuetype) == issuetype:
                self.__display_issue(issue)
                if issue.fields.subtasks:
                    for subtask in issue.fields.subtasks:
                        if str(subtask.fields.status) == "In Progress" or str(subtask.fields.status) == "Reopened" or str(subtask.fields.status) == "Open":
                            self.__display_issue(self.jira.issue(subtask.id), 1)

    def display_issues_for_project(self, project):
        general_issuetypes = ["Feature", "Improvement"]
        other_issuetypes = ["Pronto", "Trainings", "General work", "Maintenance"]

        for issuetype in general_issuetypes:
            print issuetype.upper() + "S"
            print "--------------------------------------------"
            self.get_all_issue_of_issuetype(project, issuetype)

        for issuetype in other_issuetypes:
            print issuetype.upper() + "S"
            print "--------------------------------------------"
            self.get_all_issue_of_issuetype(project, issuetype)

    def display_worklogs_for_sprint(self, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        dates = self.__generate_date_list(sprint_dates[0], sprint_dates[1])
        issues = self.fetch_all_issues_for_project("OMCPMNLOMG")

        for date in dates:
            print "Display worklog for {}".format(date)
            print "--------------------------------------------"
            for issue in issues:
                self.__display_issue(issue)
                self.show_worklog_for_issue(issue.key, date)

    def show_worklog_for_issue(self, key, date):
        for worklog in self.jira.worklogs(key):
            work = self.jira.worklog(key, worklog.id)
            if str(work.author.name) == "pdelos" and str(work.started).startswith(date):
                print "--------------------------------------------"
                print "| Author: {}".format(work.author)
                print "| Date: {}".format(work.started)
                print "| Time Spent: {}".format(work.timeSpent)
                print "--------------------------------------------"

    def __generate_date_list(self, start, end):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        dates = []
        for day in range(0, (end-start).days):
            date = start + datetime.timedelta(days=day)
            if date.weekday() not in [5, 6]:
                dates.append(date.strftime("%Y-%m-%d"))

        return dates

    def __get_start_and_end_date_for_sprint(self, sprint_id):
        sprint_date = {
            "1602.1": ["2016-01-13", "2016-01-26"],
            "1602.2": ["2016-01-27", "2016-02-16"],
            "1603.1": ["2016-02-17", "2016-03-01"]
        }.get(sprint_id, None)

        if sprint_date is None:
            raise RuntimeError("{} is not a proper sprint id.".format(sprint_id))

        return sprint_date

class Formatter(object):
    def __init__(self):
        self.types = {}
        self.htchar = '\t'
        self.lfchar = '\n'
        self.indent = 0
        self.set_formater(object, self.__class__.format_object)
        self.set_formater(dict, self.__class__.format_dict)
        self.set_formater(list, self.__class__.format_list)
        self.set_formater(tuple, self.__class__.format_tuple)

    def set_formater(self, obj, callback):
        self.types[obj] = callback

    def __call__(self, value, **args):
        for key in args:
            setattr(self, key, args[key])
        formater = self.types[type(value) if type(value) in self.types else object]
        return formater(self, value, self.indent)

    def format_object(self, value, indent):
        return repr(value)

    def format_dict(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + repr(key) + ': ' +
            (self.types[type(value[key]) if type(value[key]) in self.types else object])(self, value[key], indent + 1)
            for key in value
        ]
        return '{%s}' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_list(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(self, item, indent + 1)
            for item in value
        ]
        return '[%s]' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_tuple(self, value, indent):
        items = [
            self.lfchar + self.htchar * (indent + 1) + (self.types[type(item) if type(item) in self.types else object])(self, item, indent + 1)
            for item in value
        ]
        return '(%s)' % (','.join(items) + self.lfchar + self.htchar * indent)