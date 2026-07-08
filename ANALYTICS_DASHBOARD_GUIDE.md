# Analytics Dashboard - Implementation Guide

## Project Overview
The Analytics Dashboard is a professional, real-time analytics interface for recruiters on the Online Coding Assessment Platform. It displays live data from candidate performance and contest management with no hardcoded data.

## Architecture

### Technology Stack
- **Backend**: Django REST API (Python)
- **Frontend**: Chart.js (vanilla JavaScript), HTML5, CSS3
- **Database**: SQLite (live data from existing models)
- **Design**: Glassmorphism with gradients, responsive layout

### Database Models Used
1. **Submissions** - Candidate code submissions
2. **Results** - Assessment results
3. **Contest** - Contest information
4. **Assessment** - Assessment details
5. **User** - Candidate and recruiter accounts

## Features

### Section 1: Candidate Performance

#### Bar Chart
- **Data Source**: Live from Submissions & Results tables
- **Visualization**: Chart.js Bar Chart
- **X-Axis**: Candidate Names (sorted by score)
- **Y-Axis**: Candidate Scores (0-100)
- **Pagination**: 15 candidates per page with Previous/Next buttons
- **Auto-refresh**: Every 30 seconds

#### Analytics Card
Shows:
- Total Candidates
- Highest Score & Scorer Name
- Lowest Score
- Average Score
- Pass Rate with Passed/Failed breakdown
- Score Distribution (0-20, 21-40, 41-60, 61-80, 81-100)

### Section 2: Contest Analytics

#### Line Chart
- **Data Source**: Live from Contest table
- **Visualization**: Chart.js Line Chart
- **X-Axis**: Months (Jan-Dec)
- **Y-Axis**: Contest Count
- **Period**: Last 12 months
- **Auto-refresh**: Every 30 seconds

#### Analytics Card
Shows:
- Total Contests
- Current Month Contests
- Average Contests per Month
- Most Active Month
- Growth Rate (Month-over-Month)

## File Structure

```
recruiter/
├── views.py                # Backend API endpoints (4 new functions)
├── urls.py                 # URL routing for reports

templates/
├── recruiter/
    ├── reports.html        # Main dashboard template
```

## API Endpoints

All endpoints are protected and require staff/recruiter authentication.

### 1. Get Candidate Performance (Paginated)
**Endpoint**: `/recruiter/reports/api/candidate-performance/`
**Method**: GET
**Parameters**:
- `page` (int): Page number (default: 1)
- `per_page` (int): Records per page (default: 15, max: 100)

**Response**:
```json
{
  "success": true,
  "candidates": [
    {
      "name": "john_doe",
      "score": 95.5,
      "rank": 1
    },
    {
      "name": "jane_smith",
      "score": 87.3,
      "rank": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "per_page": 15,
    "total_candidates": 142,
    "has_previous": false,
    "has_next": true
  }
}
```

### 2. Get Candidate Statistics
**Endpoint**: `/recruiter/reports/api/candidate-stats/`
**Method**: GET

**Response**:
```json
{
  "success": true,
  "stats": {
    "total_candidates": 142,
    "highest_score": 100,
    "lowest_score": 15.5,
    "average_score": 72.3,
    "highest_scorer": "john_doe",
    "passed_candidates": 98,
    "failed_candidates": 44,
    "pass_percentage": 69.01,
    "score_distribution": {
      "0-20": 5,
      "21-40": 12,
      "41-60": 25,
      "61-80": 60,
      "81-100": 40
    }
  }
}
```

### 3. Get Contest Analytics
**Endpoint**: `/recruiter/reports/api/contest-analytics/`
**Method**: GET

**Response**:
```json
{
  "success": true,
  "data": [
    {"month": "Jan", "count": 3},
    {"month": "Feb", "count": 5},
    {"month": "Mar", "count": 4},
    ...
  ]
}
```

### 4. Get Contest Statistics
**Endpoint**: `/recruiter/reports/api/contest-stats/`
**Method**: GET

**Response**:
```json
{
  "success": true,
  "stats": {
    "total_contests": 45,
    "current_month_contests": 5,
    "avg_contests_per_month": 3.75,
    "most_active_month": "October",
    "least_active_month": "June",
    "growth_rate": 25.5
  }
}
```

## How It Works

### Data Flow

1. **User Access**
   - Recruiter logs in and navigates to `/recruiter/reports/`
   - Dashboard renders template with loading skeletons

2. **Initial Load**
   - JavaScript makes 4 parallel API calls
   - Receives live data from database
   - Renders charts and statistics

3. **Auto-Refresh**
   - Every 30 seconds, all 4 endpoints are queried
   - Charts animate to new values
   - Statistics update in real-time

4. **Pagination**
   - Candidate bar chart shows 15 candidates per page
   - Previous/Next buttons update the page number
   - Chart re-renders without page reload

### Real-Time Updates

The dashboard automatically updates when:
- Candidate submits code (Submission created)
- Scores are evaluated (Submission/Result updated)
- Results are published (Result status changes)
- Contest is created/modified (Contest table updated)

Data flows through live database queries with no caching required.

## UI/UX Features

### Design System
- **Glassmorphism**: Semi-transparent cards with backdrop blur
- **Color Palette**: 
  - Primary: Cyan (#00fff7)
  - Secondary: Pink (#ff2d78)
  - Accent: Purple (#b026ff)
  - Background: Deep void (#0a0a14)

### Responsive Breakpoints
- **Desktop**: Full 2-column layout (Left: Chart, Right: Analytics)
- **Tablet**: Stack on smaller screens
- **Mobile**: Single column with optimized controls

### Animations
- **Page Load**: Fade-in animation (0.6s ease-out)
- **Charts**: Smooth rendering with transition effects
- **Interactions**: Hover effects on cards and buttons
- **Loading**: Skeleton loaders with shimmer animation

### Accessibility
- Proper contrast ratios
- Keyboard navigation support
- ARIA labels for screen readers
- Semantic HTML structure

## Performance Optimizations

1. **Pagination**: Limits data per request to 15 candidates
2. **Lazy Loading**: Charts load on-demand
3. **Efficient Queries**: Uses Django ORM aggregations
4. **Caching**: Could be added for 5-10 minute cache
5. **Minification**: All CSS/JS inline for single HTTP request

## Testing

### Manual Testing Steps

1. **Access Dashboard**
   ```
   URL: http://localhost:8000/recruiter/reports/
   Requires: Staff/Recruiter login
   ```

2. **Test Bar Chart**
   - Load page and verify bar chart renders
   - Check all candidate names display correctly
   - Hover over bars and verify tooltips
   - Click Previous/Next and verify pagination

3. **Test Line Chart**
   - Scroll down to contest analytics
   - Verify line chart shows monthly trends
   - Check all 12 months display

4. **Test Auto-Refresh**
   - Modify data in admin panel
   - Wait 30 seconds
   - Verify dashboard updates automatically

5. **Test Responsive Design**
   - Resize browser to tablet size
   - Verify layout stacks correctly
   - Check all buttons remain accessible

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment Considerations

1. **Static Files**
   - Ensure Chart.js CDN is accessible
   - Or download and serve locally

2. **Database Indexes**
   - Consider indexing on:
     - Submission.user_id
     - Submission.score
     - Result.candidate_id
     - Result.score
     - Contest.start_time

3. **Query Optimization**
   - Use select_related() for foreign keys
   - Use prefetch_related() for reverse relations
   - Consider database query caching

4. **Security**
   - Protected by is_staff check
   - CSRF protection enabled
   - XSS prevention with Django templates

## Future Enhancements

1. **Advanced Filters**
   - Filter by assessment type
   - Filter by date range
   - Filter by candidate group/batch

2. **Export Features**
   - Export to CSV/Excel
   - Generate PDF reports
   - Schedule automated reports

3. **Advanced Analytics**
   - Candidate skill breakdown
   - Problem difficulty analysis
   - Time-to-completion metrics
   - Success rate trends

4. **Customization**
   - Custom chart types (Pie, Radar, Doughnut)
   - Customizable time ranges
   - Saved report templates
   - Email notifications

## Troubleshooting

### Charts Not Loading
- Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible
- Confirm API endpoints return valid JSON

### Data Not Updating
- Verify database has actual data
- Check API response status (200 OK)
- Ensure auto-refresh interval is set (30s)

### Pagination Issues
- Verify page parameter in URL
- Check per_page calculation is correct
- Confirm total_pages calculation matches

### Performance Issues
- Check database query times
- Monitor API response times
- Consider adding query optimization/caching

## Support & Maintenance

For issues or questions:
1. Check browser console for errors
2. Review API responses in Network tab
3. Verify database connectivity
4. Check Django logs for backend errors

---

**Last Updated**: July 8, 2026
**Version**: 1.0
**Status**: Production Ready
