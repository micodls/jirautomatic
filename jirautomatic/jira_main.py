from jira import JIRA

class JiraLogger:
    def __init__(self):
        jira = JIRA(server="http://jira3.inside.nsn.com", basic_auth=("pdelos", "January@2016"));
        print jira.projects()