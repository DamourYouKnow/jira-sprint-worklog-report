import xml.etree.ElementTree as ElementTree


class TeamMember:
    def __init__(self, name):
        self.name = name
        self.issues = []
        
    def total_logged_time(self):
        return sum(issue.logged_time for issue in self.issues)

class Issue:
    def __init__(
        self,
        id,
        summary,
        url,
        assignee,
        logged_time,
        parent,
        subtasks
    ):
        self.id = id
        self.summary = summary
        self.url = url
        self.assignee = assignee
        self.logged_time = logged_time
        self.parent = parent
        self.subtasks = subtasks

    def __str__(self):
        return ' - '.join([
            self.id,
            self.assignee,
            str(self.logged_time)
        ])


def generate_report():
    # Get items
    current_sprint = load_xml('./data/sprint-tasks.xml')
    subtasks = load_xml('./data/all-subtasks.xml')

    # Load main issues
    issues = { issue.id : issue for issue in current_sprint }

    # Filter out subtasks not in sprint
    subtasks = [subtask for subtask in subtasks if subtask.parent in issues]

    # Merge filtered subtasks with main issues
    issues = {**issues, **{ issue.id : issue for issue in subtasks }}

    # Generate report data
    report = {}

    for issue in issues.values():
        if issue.assignee not in report:
            report[issue.assignee] = TeamMember(issue.assignee)

        report[issue.assignee].issues.append(issue)

    output = format_report(report)


def create_issue(item):
    logged_time = 0
    xml_logged_time = item.find('timespent')
    if xml_logged_time is not None:
        logged_time = int(xml_logged_time.attrib['seconds'])

    return Issue(
        item.find('key').text,
        item.find('summary').text,
        item.find('link').text,
        item.find('assignee').text,
        logged_time,
        None if item.find('parent') is None else item.find('parent').text,
        [subtask.text for subtask in item.find('subtasks')]
    )


def format_report(report):
    output = []
    
    for member in report.values():
        output.append(f'{member.name} - {time_str(member.total_logged_time())}')

        for issue in member.issues:
            output.append(str(issue))

        output.append('')
    
    print('\n'.join(output))
    return '\n'.join(output)


def load_xml(filepath):
    xml = ElementTree.parse(filepath)
    items = xml.findall('channel')[0].findall('item')    
    issues = [create_issue(item) for item in items]
    return issues


def time_str(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours}h {minutes}m'


generate_report()
