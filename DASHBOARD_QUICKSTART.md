# Quick Start Guide - Analytics Dashboard

## Installation & Setup

### 1. Ensure Database Migrations
```bash
python manage.py migrate
```

### 2. Create Test Data (Optional)
To test the dashboard with sample data, run:
```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth import get_user_model
from submissions.models import Submission
from questions.models import Question, Assessment
from contest.models import Contest
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

# Create test admin/recruiter
admin, _ = User.objects.get_or_create(
    username='recruiter',
    defaults={
        'email': 'recruiter@logicl abs.com',
        'is_staff': True,
        'is_superuser': False,
    }
)
admin.set_password('recruiter123')
admin.save()

# Create test candidates
for i in range(20):
    user, _ = User.objects.get_or_create(
        username=f'candidate{i}',
        defaults={'email': f'candidate{i}@logicl abs.com'}
    )
    user.set_password('password123')
    user.save()

print("Test data created successfully!")
exit()
```

### 3. Create Django Admin Account
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 4. Start Development Server
```bash
python manage.py runserver
```

### 5. Access Dashboard
- **Admin**: http://localhost:8000/admin/ (create/manage data)
- **Recruiter Reports**: http://localhost:8000/recruiter/reports/
  - Login with credentials: `recruiter` / `recruiter123`

## URL Mapping

| Path | Purpose |
|------|---------|
| `/recruiter/reports/` | Main dashboard page |
| `/recruiter/reports/api/candidate-performance/?page=1&per_page=15` | Candidate bar chart data |
| `/recruiter/reports/api/candidate-stats/` | Candidate statistics |
| `/recruiter/reports/api/contest-analytics/` | Contest monthly trends |
| `/recruiter/reports/api/contest-stats/` | Contest statistics |

## File Locations

```
OCAP/
├── recruiter/
│   ├── views.py              # Contains all API endpoints
│   ├── urls.py               # Routes for reports
│   └── __init__.py
│
├── templates/
│   └── recruiter/
│       └── reports.html      # Dashboard UI
│
├── ANALYTICS_DASHBOARD_GUIDE.md
└── db.sqlite3                # Database
```

## Key Features

✅ **Real-Time Data**: No dummy data - all live from database
✅ **Automatic Updates**: Refreshes every 30 seconds
✅ **Pagination**: 15 candidates per page
✅ **Responsive**: Works on desktop, tablet, mobile
✅ **Professional Design**: Glassmorphism with gradients
✅ **Multiple Charts**: Bar chart for candidates, Line chart for contests
✅ **Analytics Cards**: Comprehensive statistics for each section
✅ **Light/Dark Mode**: Responsive to system theme

## Testing the API

### Using cURL
```bash
# Test candidate performance
curl "http://localhost:8000/recruiter/reports/api/candidate-performance/?page=1&per_page=15"

# Test candidate stats
curl "http://localhost:8000/recruiter/reports/api/candidate-stats/"

# Test contest analytics
curl "http://localhost:8000/recruiter/reports/api/contest-analytics/"

# Test contest stats
curl "http://localhost:8000/recruiter/reports/api/contest-stats/"
```

### Using Browser DevTools
1. Open Dashboard: http://localhost:8000/recruiter/reports/
2. Open DevTools (F12)
3. Go to Network tab
4. Watch API calls as page loads
5. Verify all 4 endpoints return 200 OK

## Customization

### Change Refresh Interval
Edit `templates/recruiter/reports.html`:
```javascript
// Line ~250
const AUTO_REFRESH_INTERVAL = 30000; // milliseconds
```

### Change Candidates Per Page
Edit `templates/recruiter/reports.html`:
```javascript
// Line ~210
let candidatePerPage = 15; // Change this value
```

### Modify Colors
Edit style section in `templates/recruiter/reports.html`:
```css
:root {
    --neon-cyan: #00fff7;      /* Primary color */
    --neon-pink: #ff2d78;      /* Secondary color */
    --neon-purple: #b026ff;    /* Accent color */
}
```

## Troubleshooting

### Issue: "Page not found" error
**Solution**: Ensure URLs are properly configured
```bash
python manage.py check
```

### Issue: Charts not rendering
**Solution**: Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible
- Check API endpoints in Network tab

### Issue: No data displayed
**Solution**: Ensure database has data
- Go to Admin panel: http://localhost:8000/admin/
- Create test submissions and contests
- Verify data appears in dashboard after 30 seconds

### Issue: Login redirects to login page
**Solution**: User must be staff/recruiter
```python
# In Django shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='recruiter')
user.is_staff = True
user.save()
```

## Performance Tips

1. **Add Database Indexes**
   ```python
   # In models.py
   class Meta:
       indexes = [
           models.Index(fields=['-score']),
           models.Index(fields=['user']),
       ]
   ```

2. **Enable Query Caching**
   - Add caching middleware for 5-minute TTL
   - Cache API responses in browser (HTTP cache headers)

3. **Optimize Images**
   - Use WebP format for charts
   - Compress static assets

4. **Monitor Performance**
   - Use Django Debug Toolbar
   - Check database query times
   - Monitor browser performance (DevTools)

---

**Next Steps**:
1. ✅ Run migrations
2. ✅ Create test data
3. ✅ Start development server
4. ✅ Access dashboard
5. ✅ Test all features
6. ✅ Deploy to production

For more details, see `ANALYTICS_DASHBOARD_GUIDE.md`
