from jira import JIRA

class JiraLogger:
    def __init__(self):
        self.jira = JIRA(server="http://jira3.int.net.nokia.com", basic_auth=("pdelos", "January@2016"));
        # Get all projects viewable by anonymous users.
        projects = self.jira.projects()

        # Sort available project keys, then return the second, third, and fourth keys.
        keys = sorted([project.key for project in projects])[2:5]

        issues = self.jira.search_issues("project=OMCPMNLOMG")
        print self.get_all_issues_for_project("OMCPMNLOMG")

    def get_all_issues_for_project(self, project):
        return self.jira.search_issues("project={}".format(project))