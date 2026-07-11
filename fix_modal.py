import re

for filename in ['contest_create_objective.html', 'contest_create_interactive.html']:
    filepath = 'templates/recruiter/' + filename
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Inject bg-layer
    if 'class="bg-layer"' not in content:
        content = content.replace('<body>', '<body>\n\n<!-- Background glow layer -->\n<div class="bg-layer"></div>\n')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated bg-layer in', filename)

filepath = 'templates/recruiter/contests_list.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if 'class="bg-layer"' not in content:
    content = content.replace('<body>', '<body>\n\n<!-- Background glow layer -->\n<div class="bg-layer"></div>\n')

# Change button
content = content.replace('<a href="{% url \'recruiter_contest_create\' %}" class="btn-create">+ Create Contest</a>', '<button class="btn-create" onclick="openCreateModal()">+ Create Contest</button>')

# Add Modal CSS
modal_css = '''
        /* MODAL CSS */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(3, 6, 17, 0.8);
            backdrop-filter: blur(8px);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-content {
            background: rgba(12, 8, 28, 0.95);
            border: 1px solid rgba(0, 114, 255, 0.3);
            border-radius: 12px;
            padding: 30px;
            width: 90%;
            max-width: 800px;
            position: relative;
            box-shadow: 0 0 25px rgba(0, 114, 255, 0.2);
        }
        .modal-close {
            position: absolute;
            top: 15px;
            left: 15px; /* User asked for top-left exit navigation */
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 5px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .modal-close:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        .format-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(0, 114, 255, 0.15);
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: 0.3s;
            text-decoration: none;
            display: block;
            color: var(--text-primary);
        }
        .format-card:hover {
            border-color: var(--neon-cyan);
            transform: translateY(-5px);
            color: var(--text-primary);
            background: rgba(0, 114, 255, 0.05);
        }
        .format-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: var(--neon-purple);
        }
        .modal-header-text {
            text-align: center;
            margin-bottom: 30px;
            padding-top: 10px;
        }
'''
if 'MODAL CSS' not in content:
    content = content.replace('</style>', modal_css + '\n</style>')

# Add Modal HTML and JS
modal_html = '''
<!-- Create Contest Modal -->
<div class="modal-overlay" id="createContestModal">
    <div class="modal-content">
        <button class="modal-close" onclick="closeCreateModal()"><i class="fas fa-times"></i> Close</button>
        
        <div class="modal-header-text">
            <div class="page-title">// CREATE NEW CONTEST</div>
            <div class="page-heading">Select Contest Format</div>
        </div>

        <div class="row g-4">
            <div class="col-md-6">
                <a href="{% url 'recruiter_contest_create_objective' %}" class="format-card">
                    <div class="format-icon"><i class="fas fa-list-ul"></i></div>
                    <h4>Objective Format</h4>
                    <p class="text-muted" style="font-size: 0.85rem;">Create a contest with Multiple Choice Questions (MCQs).</p>
                </a>
            </div>
            <div class="col-md-6">
                <a href="{% url 'recruiter_contest_create_interactive' %}" class="format-card">
                    <div class="format-icon"><i class="fas fa-laptop-code"></i></div>
                    <h4>Interactive Format</h4>
                    <p class="text-muted" style="font-size: 0.85rem;">Create a coding contest with Programming Questions and Test Cases.</p>
                </a>
            </div>
        </div>
    </div>
</div>

<script>
    function openCreateModal() {
        document.getElementById('createContestModal').classList.add('active');
    }
    function closeCreateModal() {
        document.getElementById('createContestModal').classList.remove('active');
    }
</script>
</body>
'''
if 'id="createContestModal"' not in content:
    content = content.replace('</body>', modal_html)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated contests_list.html completely')
