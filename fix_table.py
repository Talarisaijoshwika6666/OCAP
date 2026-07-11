import re

filepath = 'templates/recruiter/contests_list.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix table header
old_table_head = '''                    <tr>
                        <th>NAME</th>
                        <th>TOPIC</th>
                        <th>STARTS</th>
                        <th>DURATION</th>
                        <th>MCQS</th>
                        <th>PROG. QS</th>
                        <th>REGISTERED</th>
                        <th>STATUS</th>
                    </tr>'''
new_table_head = '''                    <tr>
                        <th>NAME</th>
                        <th>TOPIC</th>
                        <th>STARTS</th>
                        <th>DURATION</th>
                        <th>FORMAT</th>
                        <th>REGISTERED</th>
                        <th>STATUS</th>
                    </tr>'''
content = content.replace(old_table_head, new_table_head)

# Fix table row
old_table_row = '''                    <tr>
                        <td>{{ c.title }}</td>
                        <td>{{ c.topic }}</td>
                        <td>{{ c.start_time|date:"Y-m-d H:i" }}</td>
                        <td>{{ c.duration_minutes }} mins</td>
                        <td>{{ c.mcqquestion_set.count|default:"0" }}</td>
                        <td>{{ c.programmingquestion_set.count|default:"0" }}</td>
                        <td>0</td>
                        <td>{% if c.is_active %}Active{% else %}Inactive{% endif %}</td>
                    </tr>'''
new_table_row = '''                    <tr class="contest-row">
                        <td class="contest-title">{{ c.title }}</td>
                        <td class="contest-topic">{{ c.topic }}</td>
                        <td>{{ c.start_time|date:"Y-m-d H:i" }}</td>
                        <td>{{ c.duration_minutes }} mins</td>
                        <td class="contest-format">{{ c.get_format_type_display }}</td>
                        <td>0</td>
                        <td>{% if c.is_active %}<span class="badge bg-success">Active</span>{% else %}<span class="badge bg-secondary">Inactive</span>{% endif %}</td>
                    </tr>'''
content = content.replace(old_table_row, new_table_row)

# Add search bar
old_title_div = '''    <div class="contests-table-container">
        <div class="page-title mb-3">// YOUR CONTESTS</div>'''
new_title_div = '''    <div class="contests-table-container">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="page-title m-0">// YOUR CONTESTS</div>
            <div class="search-box d-flex align-items-center px-3" style="background: rgba(12,8,28,0.6); border: 1px solid rgba(0,114,255,0.25); border-radius: 20px; transition: all 0.2s;" onfocusin="this.style.borderColor='var(--neon-cyan)';" onfocusout="this.style.borderColor='rgba(0,114,255,0.25)';">
                <i class="fas fa-search" style="color: var(--neon-cyan); font-size: 0.8rem;"></i>
                <input type="text" id="contestSearchInput" placeholder="Filter contests..." class="form-control bg-transparent border-0 text-white shadow-none ps-2 py-1" style="font-size: 0.8rem; width: 180px;" onkeyup="filterContests()">
            </div>
        </div>'''
content = content.replace(old_title_div, new_title_div)

# Add JS filter logic
js_logic = '''<script>
    function openCreateModal() {
        document.getElementById('createContestModal').classList.add('active');
    }
    function closeCreateModal() {
        document.getElementById('createContestModal').classList.remove('active');
    }
    function filterContests() {
        let input = document.getElementById('contestSearchInput').value.toLowerCase();
        let rows = document.querySelectorAll('.contest-row');
        rows.forEach(row => {
            let title = row.querySelector('.contest-title').innerText.toLowerCase();
            let topic = row.querySelector('.contest-topic').innerText.toLowerCase();
            let format = row.querySelector('.contest-format').innerText.toLowerCase();
            if (title.includes(input) || topic.includes(input) || format.includes(input)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
</script>'''
content = content.replace('''<script>
    function openCreateModal() {
        document.getElementById('createContestModal').classList.add('active');
    }
    function closeCreateModal() {
        document.getElementById('createContestModal').classList.remove('active');
    }
</script>''', js_logic)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
