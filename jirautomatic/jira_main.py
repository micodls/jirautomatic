from jira import JIRA

class JiraLogger:
    def __init__(self):
        self.jira = JIRA(server="http://jira3.int.net.nokia.com", basic_auth=("pdelos", "January@2016"));
        # Get all projects viewable by anonymous users.
        projects = self.jira.projects()

        # Sort available project keys, then return the second, third, and fourth keys.
        keys = sorted([project.key for project in projects])[2:5]

        print self.display_issues_for_project("OMCPMNLOMG")

    def get_all_issues_for_project(self, project):
        return self.jira.search_issues("project={}".format(project), maxResults=False)

    def format_issue_display(self, issue, tabbing=1):
        print "Id: {}".format(issue.key)
        print "Summary: {}".format(issue.fields.summary)
        print "Assignee: {}".format(issue.fields.assignee)
        print "Reporter: {}".format(issue.fields.reporter)
        print "Status: {}".format(issue.fields.status)

    def get_all_issue_of_issuetype(self, issues, issuetype):
        for issue in issues:
            if str(issue.fields.status) == "In Progress" and str(issue.fields.issuetype) == issuetype:
                    self.format_issue_display(issue)
                    if issue.fields.subtasks:
                        self.get_all_issue_of_issuetype(issues, "Sub-task")
                    print "============================================"

    def display_issues_for_project(self, project):
        general_issuetypes = ["Feature", "Improvement"]
        other_issuetypes = ["Pronto", "Trainings", "General work", "Maintenance"]
        issues = self.get_all_issues_for_project(project) # SNIMissingWarning and InsecurePlatformWarning is printed everything a query is called. This is just to suppress the warning for a while.

        for issuetype in general_issuetypes:
            print issuetype.upper() + "S"
            print "============================================"
            self.get_all_issue_of_issuetype(issues, issuetype)

        for issuetype in other_issuetypes:
            print issuetype.upper() + "S"
            print "============================================"
            self.get_all_issue_of_issuetype(issues, issuetype)