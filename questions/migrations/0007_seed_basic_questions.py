from django.db import migrations


QUESTIONS = [
    {
        'title': 'Print Hello World',
        'description': 'Write a program that prints the exact text "Hello, World!" to standard output.',
        'topic': 'General',
        'difficulty': 'Easy',
        'sample_input': '',
        'sample_output': 'Hello, World!',
    },
    {
        'title': 'Sum of Two Numbers',
        'description': 'Read two integers from input, separated by a space, and print their sum.',
        'topic': 'Basics',
        'difficulty': 'Easy',
        'sample_input': '3 5',
        'sample_output': '8',
    },
    {
        'title': 'Reverse a String',
        'description': 'Read a string and print it reversed.',
        'topic': 'Strings',
        'difficulty': 'Easy',
        'sample_input': 'hello',
        'sample_output': 'olleh',
    },
    {
        'title': 'Check Palindrome',
        'description': 'Read a string and print "Yes" if it reads the same forwards and backwards, otherwise print "No".',
        'topic': 'Strings',
        'difficulty': 'Easy',
        'sample_input': 'madam',
        'sample_output': 'Yes',
    },
    {
        'title': 'Find Maximum in Array',
        'description': 'Read a list of space-separated integers and print the largest value.',
        'topic': 'Arrays',
        'difficulty': 'Easy',
        'sample_input': '4 9 2 7 1',
        'sample_output': '9',
    },
    {
        'title': 'Factorial of a Number',
        'description': 'Read a non-negative integer n and print n! (the factorial of n).',
        'topic': 'Basics',
        'difficulty': 'Easy',
        'sample_input': '5',
        'sample_output': '120',
    },
    {
        'title': 'Fibonacci Series',
        'description': 'Read an integer n and print the first n numbers of the Fibonacci sequence, space-separated, starting from 0.',
        'topic': 'Basics',
        'difficulty': 'Medium',
        'sample_input': '6',
        'sample_output': '0 1 1 2 3 5',
    },
    {
        'title': 'Check Prime Number',
        'description': 'Read an integer and print "Prime" if it is a prime number, otherwise print "Not Prime".',
        'topic': 'Basics',
        'difficulty': 'Medium',
        'sample_input': '7',
        'sample_output': 'Prime',
    },
    {
        'title': 'Count Vowels in a String',
        'description': 'Read a string and print the number of vowels (a, e, i, o, u — case-insensitive) it contains.',
        'topic': 'Strings',
        'difficulty': 'Easy',
        'sample_input': 'Hello World',
        'sample_output': '3',
    },
    {
        'title': 'Swap Two Numbers',
        'description': 'Read two integers, swap their values without using a third variable, and print them space-separated in swapped order.',
        'topic': 'Basics',
        'difficulty': 'Easy',
        'sample_input': '10 20',
        'sample_output': '20 10',
    },
]


def seed_questions(apps, schema_editor):
    Question = apps.get_model('questions', 'Question')
    for q in QUESTIONS:
        Question.objects.get_or_create(
            title=q['title'],
            defaults={
                'description': q['description'],
                'topic': q['topic'],
                'difficulty': q['difficulty'],
                'sample_input': q['sample_input'],
                'sample_output': q['sample_output'],
            },
        )


def remove_seeded_questions(apps, schema_editor):
    Question = apps.get_model('questions', 'Question')
    titles = [q['title'] for q in QUESTIONS]
    Question.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_question_topic'),
    ]

    operations = [
        migrations.RunPython(seed_questions, remove_seeded_questions),
    ]
