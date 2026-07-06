from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
 
from contest.models import Contest
from questions.models import Question, TestCase
 
 
DEMO_QUESTIONS = [
    {
        "title": "Two Sum",
        "description": "Given an array of integers and a target, print the indices of the two numbers "
                        "that add up to the target, space separated.\n\n"
                        "Read the array (space separated ints) on line 1 and the target on line 2. "
                        "Print the two indices on one line, space separated.",
        "difficulty": "Easy",
        "sample_input": "2 7 11 15\n9",
        "sample_output": "0 1",
    },
    {
        "title": "Reverse a String",
        "description": "Read a single line string and print it reversed.",
        "difficulty": "Easy",
        "sample_input": "hello",
        "sample_output": "olleh",
    },
    {
        "title": "Fibonacci Number",
        "description": "Read an integer n and print the n-th Fibonacci number (0-indexed, "
                        "F(0)=0, F(1)=1).",
        "difficulty": "Medium",
        "sample_input": "10",
        "sample_output": "55",
    },
]
 
 
class Command(BaseCommand):
    help = "Seed a live, an upcoming, and a past contest with demo problems for testing."
 
    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes", type=int, default=60 * 24 * 7,
            help="How long the live demo contest should run for (default = 1 week).",
        )
 
    def handle(self, *args, **options):
        now = timezone.now()
 
        questions = []
        for q in DEMO_QUESTIONS:
            obj, created = Question.objects.get_or_create(
                title=q["title"],
                defaults={
                    "description": q["description"],
                    "difficulty": q["difficulty"],
                    "sample_input": q["sample_input"],
                    "sample_output": q["sample_output"],
                    "time_limit": 30,
                },
            )
            if created:
                TestCase.objects.create(
                    question=obj,
                    input_data=q["sample_input"],
                    expected_output=q["sample_output"],
                    is_hidden=False,
                )
            questions.append(obj)
            status = "created" if created else "reused"
            self.stdout.write(f"  Question '{obj.title}' {status}")
 
        duration = options["minutes"]
 
        live, _ = Contest.objects.update_or_create(
            title="LogicLabs Live Demo Contest",
            defaults={
                "description": "A demo contest running right now — solve the problems before time runs out!",
                "start_time": now - timedelta(minutes=5),
                "end_time": now + timedelta(minutes=duration),
                "is_active": True,
            },
        )
        live.questions.set(questions)
 
        upcoming, _ = Contest.objects.update_or_create(
            title="LogicLabs Weekly #42",
            defaults={
                "description": "Next week's rated contest.",
                "start_time": now + timedelta(days=2),
                "end_time": now + timedelta(days=2, minutes=90),
                "is_active": True,
            },
        )
        upcoming.questions.set(questions)
 
        past, _ = Contest.objects.update_or_create(
            title="LogicLabs Weekly #41",
            defaults={
                "description": "Last week's rated contest.",
                "start_time": now - timedelta(days=7),
                "end_time": now - timedelta(days=7) + timedelta(minutes=90),
                "is_active": True,
            },
        )
        past.questions.set(questions)
 
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. '{live.title}' is LIVE for the next {duration} minutes.\n"
            f"Visit /contest/, register for it, then click 'Take Test'."
        ))
