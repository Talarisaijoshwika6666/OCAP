import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from .models import Topic, TopicProgress
from .content_data import BASIC_SECTIONS, INTERMEDIATE_SECTIONS, TOPIC_CONTENT

User = get_user_model()

# Shared by learning_path_view and topic_detail_view so both pages stay in
# sync (module-level so it's only defined once).
LEARNING_PATHS = {
    "data-structures": {
        "title": "Data Structures",
        "icon": "fas fa-sitemap",
        "accent": "#00ff82",
        "accent_rgb": "0,255,130",
        "tagline": "Master the building blocks of efficient code",
        "topics": [
            {"title": "Arrays & Strings", "icon": "fas fa-list-ol", "difficulty": "easy", "time": "45 min", "progress": 0},
            {"title": "Linked Lists", "icon": "fas fa-link", "difficulty": "easy", "time": "40 min", "progress": 0},
            {"title": "Trees & Graphs", "icon": "fas fa-diagram-project", "difficulty": "medium", "time": "1h 30m", "progress": 0},
            {"title": "Dynamic Programming", "icon": "fas fa-layer-group", "difficulty": "hard", "time": "2h", "progress": 0},
        ],
    },
    "database": {
        "title": "Database",
        "icon": "fas fa-database",
        "accent": "#ffc107",
        "accent_rgb": "255,193,7",
        "tagline": "Design, query and optimize real-world data stores",
        "topics": [
            {"title": "SQL Basics", "icon": "fas fa-terminal", "difficulty": "easy", "time": "30 min", "progress": 0},
            {"title": "Joins & Queries", "icon": "fas fa-code-branch", "difficulty": "medium", "time": "50 min", "progress": 0},
            {"title": "Indexing", "icon": "fas fa-magnifying-glass", "difficulty": "medium", "time": "45 min", "progress": 0},
            {"title": "Query Optimization", "icon": "fas fa-gauge-high", "difficulty": "hard", "time": "1h 15m", "progress": 0},
        ],
    },
    "system-design": {
        "title": "System Design",
        "icon": "fas fa-drafting-compass",
        "accent": "#ff2d78",
        "accent_rgb": "255,45,120",
        "tagline": "Architect systems that scale",
        "topics": [
            {"title": "Scalability", "icon": "fas fa-arrows-up-down-left-right", "difficulty": "medium", "time": "1h", "progress": 0},
            {"title": "Load Balancing", "icon": "fas fa-scale-balanced", "difficulty": "medium", "time": "45 min", "progress": 0},
            {"title": "Caching", "icon": "fas fa-bolt", "difficulty": "easy", "time": "40 min", "progress": 0},
            {"title": "Microservices", "icon": "fas fa-cubes", "difficulty": "hard", "time": "1h 30m", "progress": 0},
        ],
    },
}

# Basic and Intermediate tab section definitions (key/title/icon), and the
# actual educational content for every topic, now live in content_data.py
# (BASIC_SECTIONS, INTERMEDIATE_SECTIONS, TOPIC_CONTENT). Kept out of this
# file so views.py stays focused on request handling.


# ── Learning progress helpers ──────────────────────────────────────────
# Topics are matched to their saved progress by (subject_slug, topic_slug)
# where topic_slug = slugify(topic title). Anonymous users simply see
# everything as "not started" (nothing is persisted for them).

def _progress_map(user, subject_slug):
    """{topic_slug: status} for every saved TopicProgress row of this user
    within a given subject. Empty dict for anonymous users."""
    if not user.is_authenticated:
        return {}
    rows = TopicProgress.objects.filter(user=user, subject_slug=subject_slug)
    return {row.topic_slug: row.status for row in rows}


def _with_progress(topics, progress_map):
    """Return a new list of topic dicts (shallow copies) annotated with the
    user's saved status/progress percentage, without mutating the shared
    LEARNING_PATHS module-level data."""
    annotated = []
    for t in topics:
        slug = slugify(t['title'])
        status = progress_map.get(slug, TopicProgress.NOT_STARTED)
        annotated.append({
            **t,
            'slug': slug,
            'status': status,
            'progress': TopicProgress.STATUS_PERCENT.get(status, 0),
        })
    return annotated


def _module_completion(annotated_topics):
    total = len(annotated_topics)
    completed = sum(1 for t in annotated_topics if t['status'] == TopicProgress.COMPLETED)
    percent = round((completed / total) * 100) if total else 0
    return {'total': total, 'completed': completed, 'percent': percent}


def quest_view(request):
    topics = Topic.objects.filter(category='quest').order_by('order')

def study_plan_view(request, topic):

    # Short display labels shown on the Quest overview cards where they
    # differ from the full topic title used on the Learning Path / Topic
    # pages (e.g. "Query Optimization" -> "Optimization" here), keyed by
    # (subject_slug, topic_slug).
    label_overrides = {
        ('database', 'query-optimization'): 'Optimization',
    }

    # Levels label shown under each subject icon — preserves the existing
    # (pre-existing) copy on the Quest overview cards.
    levels_labels = {
        'data-structures': '35 Levels',
        'database': '5 Levels',
        'system-design': '5 Levels',
    }

    quest_subjects = []
    for subject_slug, path_data in LEARNING_PATHS.items():
        progress_map = _progress_map(request.user, subject_slug)
        annotated = _with_progress(path_data['topics'], progress_map)
        stats = _module_completion(annotated)

        overview_topics = [
            {
                'slug': t['slug'],
                'label': label_overrides.get((subject_slug, t['slug']), t['title']),
                'status': t['status'],
            }
            for t in annotated
        ]

        quest_subjects.append({
            'slug': subject_slug,
            'title': path_data['title'],
            'icon': path_data['icon'],
            'accent': path_data['accent'],
            'accent_rgb': path_data['accent_rgb'],
            'levels_label': levels_labels.get(subject_slug, ''),
            'topics': overview_topics,
            'percent': stats['percent'],
            'completed': stats['completed'],
            'total': stats['total'],
        })

    return render(request, 'quest/quest.html', {
        'topics': topics,
        'quest_subjects': quest_subjects,
    })


def learning_path_view(request, subject):
    """
    Dedicated Learning Path page for a Quest subject (Data Structures,
    Database, System Design). Displays the topic cards for that subject.
    Topic content itself is not implemented yet — navigation + listing only.
    """

    path_data = LEARNING_PATHS.get(subject)

    if not path_data:
        raise Http404("Learning path not found")

    progress_map = _progress_map(request.user, subject)
    annotated_topics = _with_progress(path_data['topics'], progress_map)
    module_stats = _module_completion(annotated_topics)

    # Shallow copy so we don't mutate the shared LEARNING_PATHS dict.
    path_data = {**path_data, 'topics': annotated_topics}

    return render(request, 'quest/learning_path.html', {
        'subject_slug': subject,
        'path_data': path_data,
        'module_stats': module_stats,
    })


def topic_detail_view(request, subject, topic_slug):
    """
    Dedicated Topic page, e.g. Quest > Data Structures > Arrays & Strings.
    Renders breadcrumb, header, progress indicator, and the Basic /
    Intermediate tabs, each populated with the authored educational content
    for this topic from content_data.py (falls back to a "coming soon"
    placeholder per-section if a topic has no content yet).
    """

    path_data = LEARNING_PATHS.get(subject)
    if not path_data:
        raise Http404("Learning path not found")

    topic = next(
        (t for t in path_data['topics'] if slugify(t['title']) == topic_slug),
        None,
    )
    if not topic:
        raise Http404("Topic not found")

    progress_map = _progress_map(request.user, subject)
    status = progress_map.get(topic_slug, TopicProgress.NOT_STARTED)
    topic = {
        **topic,
        'slug': topic_slug,
        'status': status,
        'progress': TopicProgress.STATUS_PERCENT.get(status, 0),
    }

    # Look up the authored content for this topic (see content_data.py). If a
    # topic doesn't have content yet, fall back to an empty dict so sections
    # render their "coming soon" placeholder instead of erroring out.
    topic_content = TOPIC_CONTENT.get(topic_slug, {})
    basic_content = topic_content.get('basic', {})
    intermediate_content = topic_content.get('intermediate', {})

    basic_sections = [
        {**section, 'content': basic_content.get(section['key'])}
        for section in BASIC_SECTIONS
    ]
    intermediate_sections = [
        {**section, 'content': intermediate_content.get(section['key'])}
        for section in INTERMEDIATE_SECTIONS
    ]

    return render(request, 'quest/topic_detail.html', {
        'subject_slug': subject,
        'path_data': path_data,
        'topic': topic,
        'topic_slug': topic_slug,
        'basic_sections': basic_sections,
        'intermediate_sections': intermediate_sections,
    })

@login_required
@require_POST
def update_topic_progress(request, subject, topic_slug):
    """
    AJAX endpoint used by the Quest, Learning Path, and Topic pages to
    persist a topic's status (Not Started / In Progress / Completed) for
    the logged-in user. Expects JSON body: {"status": "in_progress"}.
    Returns the saved status plus the recalculated module completion so
    the frontend can update progress bars without a full page reload.
    """
    path_data = LEARNING_PATHS.get(subject)
    if not path_data:
        return JsonResponse({'error': 'Unknown subject'}, status=404)

    valid_slugs = {slugify(t['title']) for t in path_data['topics']}
    if topic_slug not in valid_slugs:
        return JsonResponse({'error': 'Unknown topic'}, status=404)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    status = payload.get('status')
    valid_statuses = {choice[0] for choice in TopicProgress.STATUS_CHOICES}
    if status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    progress, _ = TopicProgress.objects.update_or_create(
        user=request.user,
        subject_slug=subject,
        topic_slug=topic_slug,
        defaults={'status': status},
    )

    progress_map = _progress_map(request.user, subject)
    annotated_topics = _with_progress(path_data['topics'], progress_map)
    module_stats = _module_completion(annotated_topics)

    return JsonResponse({
        'subject': subject,
        'topic_slug': topic_slug,
        'status': progress.status,
        'progress': progress.percent,
        'module': module_stats,
    })


def study_plan_view(request, topic):
    roadmaps = {
        "data-structures": {
            "title": "Data Structures",
            "beginner": [
                "Arrays",
                "Strings",
                "Hash Maps",
                "Two Pointers"
            ],
            "intermediate": [
                "Linked Lists",
                "Stacks",
                "Queues",
                "Trees"
            ],
            "advanced": [
                "Graphs",
                "Dynamic Programming",
                "Tries",
                "Segment Trees"
            ]
        },

        "database": {
            "title": "Database",
            "beginner": [
                "SQL Basics",
                "SELECT",
                "WHERE",
                "ORDER BY"
            ],
            "intermediate": [
                "Joins",
                "GROUP BY",
                "HAVING",
                "Subqueries"
            ],
            "advanced": [
                "Indexing",
                "Normalization",
                "Transactions",
                "Optimization"
            ]
        },

        "system-design": {
            "title": "System Design",
            "beginner": [
                "Scalability",
                "Client Server",
                "Caching",
                "Load Balancer"
            ],
            "intermediate": [
                "Queues",
                "Replication",
                "CDN",
                "Sharding"
            ],
            "advanced": [
                "Microservices",
                "Distributed Systems",
                "CAP Theorem",
                "Consistency"
            ]
        }
    }

    roadmap = roadmaps.get(topic)

    return render(request, "quest/study_plan.html", {
        "roadmap": roadmap
    })

def home_view(request):
    return render(request, 'home.html')

def discuss_view(request):
    return render(request, 'discuss/discuss.html', {'posts': []})