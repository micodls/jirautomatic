import warnings
import datetime
from jira import JIRA

class JiraLogger:
    def __init__(self):
        warnings.filterwarnings("ignore") # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.
        # self.jira = JIRA(server="http://jira3.int.net.nokia.com", basic_auth=("pdelos", "January@2016"));

        # print self.show_worklog_for_issue("OMCPMNLOMG-29")
        self.display_worklogs_for_sprint("1602.2")

    def get_all_issues_for_project(self, project):
        return self.jira.search_issues("project={}".format(project), maxResults=False)

    def format_issue_display(self, issue, tabbing=0):
        tab = "\t" * tabbing
        print "{}Id: {}".format(tab, issue.key)
        print "{}Summary: {}".format(tab, issue.fields.summary)
        print "{}Assignee: {}".format(tab, issue.fields.assignee)
        print "{}Reporter: {}".format(tab, issue.fields.reporter)
        print "{}Status: {}".format(tab, issue.fields.status)

    def get_all_issue_of_issuetype(self, project, issuetype):
        for issue in self.get_all_issues_for_project(project):
            if (str(issue.fields.status) == "In Progress" or str(issue.fields.status) == "Reopened" or str(issue.fields.status) == "Open") and str(issue.fields.issuetype) == issuetype:
                self.format_issue_display(issue)
                print "============================================"
                if issue.fields.subtasks:
                    for subtask in issue.fields.subtasks:
                        if str(subtask.fields.status) == "In Progress" or str(subtask.fields.status) == "Reopened" or str(subtask.fields.status) == "Open":
                            self.format_issue_display(self.jira.issue(subtask.id), 1)
                            print "============================================"

    def display_issues_for_project(self, project):
        general_issuetypes = ["Feature", "Improvement"]
        other_issuetypes = ["Pronto", "Trainings", "General work", "Maintenance"]

        for issuetype in general_issuetypes:
            print issuetype.upper() + "S"
            print "============================================"
            self.get_all_issue_of_issuetype(project, issuetype)

        for issuetype in other_issuetypes:
            print issuetype.upper() + "S"
            print "============================================"
            self.get_all_issue_of_issuetype(project, issuetype)

    def display_worklogs_for_sprint(self, sprint_id):
        sprint_dates = self.__get_start_and_end_date_for_sprint(sprint_id)
        print self.__generate_date_list(sprint_dates[0], sprint_dates[1])

    def show_worklog_for_issue(self, key):
        for worklog in self.jira.worklogs(key):
            work = self.jira.worklog(key, worklog.id)
            if str(work.author.name) == "pdelos":
                print "Author: {}".format(work.author)
                print "Date: {}".format(work.created)
                print "Time Spent: {}".format(work.timeSpent)

    def __generate_date_list(self, start, end):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
        dates_list = []
        for day in range(0, (end-start).days):
            date = start + datetime.timedelta(days=day)
            if date.weekday() not in [5, 6]:
                dates_list.append(date.strftime("%Y-%m-%d"))

        return dates_list

    def __get_start_and_end_date_for_sprint(self, sprint_id):
        sprint_date = {
            "1602.1": ["2016-01-13", "2016-01-26"],
            "1602.2": ["2016-01-27", "2016-02-16"],
            "1603.1": ["2016-02-17", "2016-03-01"]
        }.get(sprint_id, None)

        if sprint_date is None:
            raise RuntimeError("{} is not a proper sprint id.".format(sprint_id))

        return sprint_date