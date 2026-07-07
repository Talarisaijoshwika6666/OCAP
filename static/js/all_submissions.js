document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('submissionSearch');
  const difficultyFilter = document.getElementById('difficultyFilter');
  const tableBody = document.getElementById('submissionTableBody');
  const rows = Array.from(tableBody.querySelectorAll('tr')).filter(row => !row.querySelector('td[colspan]'));
  const pagination = document.getElementById('pagination');
  const rowsPerPage = 10;
  let filteredRows = [...rows];
  let currentPage = 1;
  let sortKey = 'title';
  let sortDir = 'asc';

  function renderTable() {
    const query = searchInput.value.trim().toLowerCase();
    const difficulty = difficultyFilter.value.toLowerCase();

    filteredRows = rows.filter(row => {
      const text = row.textContent.toLowerCase();
      const difficultyText = row.querySelector('.difficulty-badge')?.textContent.toLowerCase() || '';
      const matchesSearch = !query || text.includes(query);
      const matchesDifficulty = difficulty === 'all' || difficultyText.includes(difficulty);
      return matchesSearch && matchesDifficulty;
    });

    filteredRows.sort((a, b) => {
      let valA = getValue(a, sortKey);
      let valB = getValue(b, sortKey);
      if (typeof valA === 'number' && typeof valB === 'number') {
        return sortDir === 'asc' ? valA - valB : valB - valA;
      }
      return sortDir === 'asc' ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
    });

    const pageCount = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));
    currentPage = Math.min(currentPage, pageCount);
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    rows.forEach(row => row.style.display = 'none');
    filteredRows.slice(start, end).forEach(row => row.style.display = '');

    renderPagination(pageCount);
  }

  function getValue(row, key) {
    switch (key) {
      case 'title':
        return row.querySelector('strong')?.textContent.trim() || '';
      case 'submissions':
        return Number(row.children[2].textContent.trim());
      case 'avgtime':
        return Number(row.children[3].textContent.trim().replace(/[^\d.]/g, '')) || 0;
      case 'rate':
        return Number((row.children[6].textContent.match(/\d+(?:\.\d+)?/) || ['0'])[0]);
      default:
        return row.textContent;
    }
  }

  function renderPagination(pageCount) {
    pagination.innerHTML = '';
    if (pageCount <= 1) return;
    const prev = document.createElement('li');
    prev.className = 'page-item' + (currentPage === 1 ? ' disabled' : '');
    prev.innerHTML = '<button class="page-link">Previous</button>';
    prev.querySelector('button').onclick = () => { if (currentPage > 1) { currentPage--; renderTable(); } };
    pagination.appendChild(prev);

    for (let i = 1; i <= pageCount; i++) {
      const item = document.createElement('li');
      item.className = 'page-item' + (i === currentPage ? ' active' : '');
      item.innerHTML = `<button class="page-link">${i}</button>`;
      item.querySelector('button').onclick = () => { currentPage = i; renderTable(); };
      pagination.appendChild(item);
    }

    const next = document.createElement('li');
    next.className = 'page-item' + (currentPage === pageCount ? ' disabled' : '');
    next.innerHTML = '<button class="page-link">Next</button>';
    next.querySelector('button').onclick = () => { if (currentPage < pageCount) { currentPage++; renderTable(); } };
    pagination.appendChild(next);
  }

  searchInput.addEventListener('input', renderTable);
  difficultyFilter.addEventListener('change', renderTable);
  document.querySelectorAll('.sort-btn').forEach(button => {
    button.addEventListener('click', () => {
      const key = button.dataset.sort;
      if (sortKey === key) {
        sortDir = sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey = key;
        sortDir = 'asc';
      }
      renderTable();
    });
  });

  document.getElementById('refreshBtn').addEventListener('click', () => {
    searchInput.value = '';
    difficultyFilter.value = 'all';
    sortKey = 'title';
    sortDir = 'asc';
    currentPage = 1;
    renderTable();
  });

  document.getElementById('exportBtn').addEventListener('click', () => {
    const headers = ['Problem Title', 'Difficulty', 'Number of Submissions', 'Average Time', 'Accepted', 'Rejected', 'Acceptance Rate', 'Last Submission'];
    const rowsCsv = filteredRows.length ? filteredRows : rows;
    const csv = [headers.join(',')].concat(rowsCsv.map(row => {
      const cells = Array.from(row.children).slice(0, 8).map(cell => '"' + cell.textContent.replace(/\s+/g, ' ').trim() + '"');
      return cells.join(',');
    })).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'all_submissions.csv';
    link.click();
  });

  document.querySelectorAll('.view-details').forEach(button => {
    button.addEventListener('click', function () {
      document.getElementById('modalTitle').textContent = this.dataset.title;
      document.getElementById('modalDifficulty').textContent = this.dataset.difficulty;
      document.getElementById('modalSubmissions').textContent = this.dataset.submissions;
      document.getElementById('modalAccepted').textContent = this.dataset.accepted;
      document.getElementById('modalRejected').textContent = this.dataset.rejected;
      document.getElementById('modalTime').textContent = this.dataset.time;
      document.getElementById('modalHighest').textContent = this.dataset.highest;
      document.getElementById('modalLowest').textContent = this.dataset.lowest;
      document.getElementById('modalLast').textContent = this.dataset.last;
    });
  });

  renderTable();
  initCharts();
});

function initCharts() {
  const data = window.dashboardData || {};
  const barCtx = document.getElementById('barChart');
  const pieCtx = document.getElementById('pieChart');
  const lineCtx = document.getElementById('lineChart');
  const modalCtx = document.getElementById('modalTrendChart');

  if (barCtx) {
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: (data.submissionsByProblem || []).map(item => item.title),
        datasets: [{ label: 'Submissions', data: (data.submissionsByProblem || []).map(item => item.count), backgroundColor: '#4f46e5' }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
  }

  if (pieCtx) {
    new Chart(pieCtx, {
      type: 'pie',
      data: {
        labels: Object.keys(data.difficultyDistribution || {}),
        datasets: [{ data: Object.values(data.difficultyDistribution || {}), backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'] }]
      },
      options: { responsive: true }
    });
  }

  if (lineCtx) {
    new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: (data.dailyTrend || []).map(item => item.label),
        datasets: [{ label: 'Daily Submissions', data: (data.dailyTrend || []).map(item => item.count), borderColor: '#2563eb', fill: false, tension: .35 }]
      },
      options: { responsive: true }
    });
  }

  if (modalCtx) {
    new Chart(modalCtx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{ label: 'Trend', data: [6, 9, 7, 11, 10, 14, 13], borderColor: '#4f46e5', fill: false, tension: .35 }]
      },
      options: { responsive: true }
    });
  }
}
