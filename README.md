# Jirautomatic
  The backend for an automated JIRA work logger that can be customized based on your needs.
  
  The inspiration for this was because our own JIRA is very slow. Rather than opening modals and new tabs, a better looking frontend and working backend was made to save the time of the engineers. Spend less time navigating thru JIRA and more time coding.

## Overview
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Features](#features)
  * [Usage](#usage)
  * [Known-Bugs](#known-bugs)
  * [To-Dos](#to-dos)
  * [Frontend](#frontend)

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

## Known Bugs
  * Adding JIRA worklog is currently unstable
    - It should return the JIRA worklog id but instead, it sometimes returns an object pointer meaning the JIRA worklog was not reflected to the server
  * Fetching worklogs per issues is very slow (takes up to 1.5hrs) when using python JIRA API.
    - Workaround for this is using curl requests in code (takes around 2 - 5 mins)
  * Passwords are not encrypted. Although passwords are not saved, security won't hurt anyone except the hackers.
  
## To-Dos
  * Support deleting issues and worklogs
  * Support for updating worklogs that are already logged.
  * Optimize fetching data from the server. Currently, it runs around 2 - 5 mins.
  * Generic sprint date generation. Currently, it is hard coded. Someone should always update the `holidays list` and `start and end sprint dates` located in `jirautomatic/helpers`

## Others
  [Frontend][frontend]
  
[pythonjira]: https://pypi.python.org/pypi/jira/
[dateutil]: https://labix.org/python-dateutil
[frontend]: http://esmz01.emea.nsn-net.net/jdecena/AutoJiraLogger
