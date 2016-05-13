# Jirautomatic
  The backend for an automated JIRA work logger that can be customized based on your needs.
  
  The inspiration for this was because our own JIRA is very slow. Rather than opening modals and new tabs, a better looking frontend and working backend was made to save the time of the engineers. Spend less time navigating thru JIRA and more time coding.

## Overview
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Features](#features)
  * [Usage](#usage)
  * [Templates](#templates)
  * [Known-Bugs-and-Issues](#known-bugs-and-issues)
  * [To-Dos](#to-dos)
  * [Others](#others)

## Requirements
  * Python 2.7 or higher
  * The following python modules:
    - [Python Jira][pythonjira]
    - [Dateutil][dateutil]

## Installation
  * Run `setup.py`
    - This takes care of the dependencies mentioned above.

## Features
  * Fetching data from JIRA server
    - Specify your personal JIRA server in `config.json`
  * Supports a few commands such as:
    - `fetch` - Gathers issues from JIRA server based on `sprint id` and `project`.
    - `log` - Logs worklog to JIRA server.
    - `test` - Tests if adding worklog works.
    - `clean` - Empties `generated` directory if ever its gets crowded.

## Usage
  * `> autojira fetch [username][password][sprint id][project]`
  * `> autojira log [username][password][file]`
  * `> autojira test [username][password]`
  * `> autojira clean`

## Templates
  * `username_sprint_id.json` - Generated file when `autojira fetch` is called.  
```json
{
    "issues": {
        "1357744": {
            "assignee": "madarra", 
            "issuetype": "General work", 
            "key": "OMCPMNLOMG-18", 
            "reporter": "madarra", 
            "sprint": "1605.2", 
            "status": "Open", 
            "subtasks": [], 
            "summary": "Scrum Master Work", 
            "worklogs": {}
        },
        "1358098": {
            "assignee": "None", 
            "issuetype": "General work", 
            "key": "OMCPMNLOMG-24", 
            "reporter": "madarra", 
            "sprint": "1605.2", 
            "status": "Open", 
            "subtasks": [], 
            "summary": "Non-Project/HR/JIRA Update/Others", 
            "worklogs": {
                "933051": {
                    "author": "pdelos", 
                    "comment": "", 
                    "started": "2016-05-04T14:19:00.000+0300", 
                    "timeSpent": "45m"
                }, 
                "933782": {
                    "author": "pdelos", 
                    "comment": "", 
                    "started": "2016-05-05T10:44:00.000+0300", 
                    "timeSpent": "45m"
                }
            }
        }
    }, 
    "sprint_end": "2016-05-17", 
    "sprint_start": "2016-05-04"
}
```
  * `some-placeholder-name.json` - File to be passed when `autojira log` is called. Note: Filename will still be discussed with frontend developer.  
```json
{
    "worklogs": [
        {
            "id": "OMCPMNLOMG-174",
            "timeSpent": "8h",
            "started": "2016-03-02",
            "comment": "SL"
        },
        {
            "id": "OMCPMNLOMG-174",
            "timeSpent": "8h",
            "started": "2016-03-02",
            "comment": "VL"
        }
    ]
}
```

## Known Bugs and Issues
  * Adding JIRA worklog is currently unstable
    - It should return the JIRA worklog id but instead, it sometimes returns an object pointer meaning the JIRA worklog was not reflected to the server
  * Fetching worklogs per issues is very slow (takes up to 1.5hrs) when using python JIRA API.
    - Workaround for this is using curl requests in code (takes around 2 - 5 mins)
  * Some warning are suppressed. I believe that these warnings can be fixed but I didn't have much time to tackle this.
  * Passwords are not encrypted. Although passwords are not saved, security won't hurt anyone except the hackers.
  * This only considers JIRA issues under an active sprint. If there is not active sprint, no issue will be generated.
  * Gathering information regarding the active sprint for an issue is hard coded. In our JIRA, sprint details is under `issue.fields.customfield_11990`. This should be changed to generic implementation.
  
## To-Dos
  * Support deleting issues and worklogs
  * Support for updating worklogs that are already logged.
  * Support for viewing non-active sprints.
  * Optimize fetching data from the server. Currently, it runs around 2 - 5 mins.
  * Generic sprint date generation. Currently, it is hard coded. Someone should always update the `holidays list` and `start and end sprint dates` located in `jirautomatic/helpers`
  * Flexibility in handling dates. Currently, dates follow the [ISO 8601][iso8601] format (Datetime with time zone : `yyyy-mm-ddThh:mm:ss.nnnnnn+|-hh:mm`). This is due to the limitations of the python JIRA API itself.

## Others
  * [Frontend][frontend]
  
[pythonjira]: https://pypi.python.org/pypi/jira/
[dateutil]: https://labix.org/python-dateutil
[frontend]: http://esmz01.emea.nsn-net.net/jdecena/AutoJiraLogger
[iso8601]: http://support.sas.com/documentation/cdl/en/lrdict/64316/HTML/default/viewer.htm#a003169814.htm
