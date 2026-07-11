import re

form_css = '''
        .form-container {
            background: rgba(12, 8, 28, 0.6);
            border: 1px solid rgba(0, 114, 255, 0.15);
            border-radius: 12px;
            padding: 24px;
        }
        .form-control, .form-select {
            background: rgba(3, 6, 17, 0.5) !important;
            border: 1px solid rgba(0, 114, 255, 0.2) !important;
            color: var(--text-primary) !important;
        }
        .form-control:focus, .form-select:focus {
            background: rgba(3, 6, 17, 0.8) !important;
            border-color: var(--neon-cyan) !important;
            color: var(--text-primary) !important;
            box-shadow: 0 0 0 0.25rem rgba(0, 245, 255, 0.25) !important;
        }
        .form-label {
            font-size: 0.85rem;
            color: rgba(224, 242, 254, 0.8);
        }
        
        .section-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(0, 114, 255, 0.2);
            padding-bottom: 10px; margin-top: 30px; margin-bottom: 20px;
        }
        .section-header h4 { font-family: var(--font-body); font-size: 1.1rem; font-weight: 600; margin: 0; }
        
        .mcq-block, .prog-block {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            position: relative;
        }
        .mcq-block-header, .prog-block-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .mcq-block-title, .prog-block-title { font-weight: 600; color: var(--neon-purple); }
        
        .btn-remove {
            background: rgba(255, 50, 50, 0.1); border: 1px solid rgba(255, 50, 50, 0.3); color: #ff6b6b; font-size: 0.8rem; padding: 4px 10px; border-radius: 4px;
        }
        .btn-remove:hover { background: rgba(255, 50, 50, 0.2); color: #ff6b6b; }
        
        .btn-add { background: rgba(112, 0, 255, 0.15); border: 1px solid var(--neon-purple); color: var(--text-primary); }
        .btn-add:hover { background: rgba(112, 0, 255, 0.3); color: white; }
        
        .btn-submit { background: linear-gradient(90deg, var(--neon-purple), var(--neon-blue)); border: none; color: white; width: 100%; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 30px; font-size: 1.1rem;}

        .tc-block {
            background: rgba(0, 0, 0, 0.2);
            border: 1px dashed rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
'''

for filename in ['contest_create_objective.html', 'contest_create_interactive.html']:
    filepath = 'templates/recruiter/' + filename
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if '.form-container' not in content:
        content = content.replace('</style>', form_css + '\n</style>')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

list_css = '''
        .contests-table-container {
            background: rgba(12, 8, 28, 0.6);
            border: 1px solid rgba(0, 114, 255, 0.15);
            border-radius: 12px;
            padding: 24px;
        }
        .table { color: var(--text-primary); background: transparent; }
        .table th { color: rgba(224, 242, 254, 0.45); font-weight: 500; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid rgba(0, 114, 255, 0.2); }
        .table td { border-bottom: 1px solid rgba(0, 114, 255, 0.1); vertical-align: middle; }
        
        .btn-create {
            background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
        }
        .btn-create:hover { color: white; opacity: 0.9; }
'''

filepath = 'templates/recruiter/contests_list.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
if '.contests-table-container' not in content:
    content = content.replace('</style>', list_css + '\n</style>')

# Fix table html
old_table_head = '''                    <tr>
                        <th>NAME</th>
                        <th>TOPIC</th>
                        <th>STARTS</th>
                        <th>DURATION</th>
                        <th>STATUS</th>
                    </tr>'''
new_table_head = '''                    <tr>
                        <th>NAME</th>
                        <th>TOPIC</th>
                        <th>STARTS</th>
                        <th>DURATION</th>
                        <th>MCQS</th>
                        <th>PROG. QS</th>
                        <th>REGISTERED</th>
                        <th>STATUS</th>
                    </tr>'''
content = content.replace(old_table_head, new_table_head)

old_table_row = '''                    <tr>
                        <td>{{ c.title }}</td>
                        <td>{{ c.topic }}</td>
                        <td>{{ c.start_time|date:"Y-m-d H:i" }}</td>
                        <td>{{ c.duration_minutes }} mins</td>
                        <td>{% if c.is_active %}Active{% else %}Inactive{% endif %}</td>
                    </tr>'''
new_table_row = '''                    <tr>
                        <td>{{ c.title }}</td>
                        <td>{{ c.topic }}</td>
                        <td>{{ c.start_time|date:"Y-m-d H:i" }}</td>
                        <td>{{ c.duration_minutes }} mins</td>
                        <td>{{ c.mcqquestion_set.count|default:"0" }}</td>
                        <td>{{ c.programmingquestion_set.count|default:"0" }}</td>
                        <td>0</td>
                        <td>{% if c.is_active %}Active{% else %}Inactive{% endif %}</td>
                    </tr>'''
content = content.replace(old_table_row, new_table_row)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
