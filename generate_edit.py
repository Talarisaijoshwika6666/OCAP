import os

with open('templates/recruiter/contest_create_objective.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Change title
content = content.replace('// CREATE OBJECTIVE CONTEST', '// EDIT OBJECTIVE CONTEST')
content = content.replace('Set up your new multiple-choice contest below.', 'Update your multiple-choice contest below.')

# Change form action
content = content.replace("""action="{% url 'recruiter_contest_create_objective' %}\"""", """action="{% url 'recruiter_contest_edit' contest.id %}\"""")

# Pre-populate fields
content = content.replace('name="title" required>', 'name="title" value="{{ contest.title }}" required>')
content = content.replace('name="topic"', 'name="topic" value="{{ contest.topic }}"')
content = content.replace('name="duration" value="30"', 'name="duration" value="{{ contest.duration_minutes }}"')

# Let's write it to contest_edit_objective.html
with open('templates/recruiter/contest_edit_objective.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('templates/recruiter/contest_create_interactive.html', 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('// CREATE INTERACTIVE CONTEST', '// EDIT INTERACTIVE CONTEST')
content2 = content2.replace("""action="{% url 'recruiter_contest_create_interactive' %}\"""", """action="{% url 'recruiter_contest_edit' contest.id %}\"""")

content2 = content2.replace('name="title" required>', 'name="title" value="{{ contest.title }}" required>')
content2 = content2.replace('name="topic"', 'name="topic" value="{{ contest.topic }}"')
content2 = content2.replace('name="duration" value="60"', 'name="duration" value="{{ contest.duration_minutes }}"')

with open('templates/recruiter/contest_edit_interactive.html', 'w', encoding='utf-8') as f:
    f.write(content2)
