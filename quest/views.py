from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Topic

User = get_user_model()

def quest_view(request):
    topics = Topic.objects.filter(category='quest').order_by('order')
    return render(request, 'quest/quest.html', {'topics': topics})

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