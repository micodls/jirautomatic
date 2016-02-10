import warnings
from jira import JIRA

class JiraLogger:
    def __init__(self):
        warnings.filterwarnings("ignore") # SNIMissingWarning and InsecurePlatformWarning is printed everytime a query is called. This is just to suppress the warning for a while.
        self.jira = JIRA(server="http://jira3.int.net.nokia.com", basic_auth=("pdelos", "January@2016"));

        print self.show_worklog_for_issue("OMCPMNLOMG-29")

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

    def show_worklog_for_issue(self, key):
        for worklog in self.jira.worklogs(key):
            work = self.jira.worklog(key, worklog.id)
            # if str(work.author) == "pdelos":
            print work.author
            print "Date: {}".format(work.created)
            print "Time Spent: {}".format(work.timeSpent)