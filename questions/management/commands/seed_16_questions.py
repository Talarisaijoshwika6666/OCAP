"""
Management command: seed_16_questions

Adds 8 Easy + 3 Medium + 5 Hard coding questions to:
  1. The practice bank  -> questions.Question   (shown on Explore/Practice page)
  2. One Assessment     -> assessments.Question (shown when a recruiter builds/edits a test)

SAFE TO RUN MULTIPLE TIMES.
Every create uses get_or_create() keyed on a unique lookup field (title, or
title+assessment), so re-running this command will never throw a
duplicate-key / IntegrityError / "conflict" error. If a question with the
same title already exists it is simply skipped (and reported), never
duplicated or overwritten.

Usage:
    python manage.py seed_16_questions
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from questions.models import Question as PracticeQuestion, TestCase as PracticeTestCase
from assessments.models import Assessment, Question as AssessmentQuestion, TestCase as AssessmentTestCase


# ---------------------------------------------------------------------------
# Question bank data
# ---------------------------------------------------------------------------
# Each entry:
#   title, topic, difficulty (Easy/Medium/Hard), description, hint, answer,
#   sample_input, sample_output, language (for the assessment copy),
#   time_limit (minutes), test_cases: list of (input_data, expected_output, is_hidden)

QUESTIONS = [
    # ------------------------- EASY (8) -------------------------
    {
        "title": "Sum of Two Numbers",
        "topic": "Basics",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read two integers A and B from input and print their sum.",
        "hint": "Use input() twice, convert to int, then add.",
        "answer": "a = int(input())\nb = int(input())\nprint(a + b)",
        "sample_input": "3\n5",
        "sample_output": "8",
        "time_limit": 15,
        "test_cases": [
            ("3\n5", "8", False),
            ("10\n20", "30", False),
            ("-4\n4", "0", True),
        ],
    },
    {
        "title": "Check Even or Odd",
        "topic": "Basics",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read an integer N and print \"Even\" if it is even, otherwise print \"Odd\".",
        "hint": "Use the modulus operator (%) with 2.",
        "answer": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')",
        "sample_input": "7",
        "sample_output": "Odd",
        "time_limit": 15,
        "test_cases": [
            ("7", "Odd", False),
            ("10", "Even", False),
            ("0", "Even", True),
        ],
    },
    {
        "title": "Reverse a String",
        "topic": "Strings",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read a string S and print it reversed.",
        "hint": "Slicing with a step of -1 reverses a string: s[::-1].",
        "answer": "s = input()\nprint(s[::-1])",
        "sample_input": "hello",
        "sample_output": "olleh",
        "time_limit": 15,
        "test_cases": [
            ("hello", "olleh", False),
            ("Python", "nohtyP", False),
            ("a", "a", True),
        ],
    },
    {
        "title": "Largest of Three Numbers",
        "topic": "Basics",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read three integers and print the largest of the three.",
        "hint": "Python's built-in max() takes multiple arguments.",
        "answer": "a = int(input())\nb = int(input())\nc = int(input())\nprint(max(a, b, c))",
        "sample_input": "4\n9\n2",
        "sample_output": "9",
        "time_limit": 15,
        "test_cases": [
            ("4\n9\n2", "9", False),
            ("1\n1\n1", "1", False),
            ("-5\n-2\n-9", "-2", True),
        ],
    },
    {
        "title": "Factorial of a Number",
        "topic": "Math",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read a non-negative integer N and print N! (N factorial).",
        "hint": "Multiply numbers from 1 to N in a loop, or use math.factorial.",
        "answer": "n = int(input())\nresult = 1\nfor i in range(2, n + 1):\n    result *= i\nprint(result)",
        "sample_input": "5",
        "sample_output": "120",
        "time_limit": 15,
        "test_cases": [
            ("5", "120", False),
            ("0", "1", False),
            ("7", "5040", True),
        ],
    },
    {
        "title": "Check Palindrome String",
        "topic": "Strings",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read a string S and print \"Yes\" if it reads the same forwards and backwards, otherwise print \"No\".",
        "hint": "Compare the string with its reverse.",
        "answer": "s = input()\nprint('Yes' if s == s[::-1] else 'No')",
        "sample_input": "madam",
        "sample_output": "Yes",
        "time_limit": 15,
        "test_cases": [
            ("madam", "Yes", False),
            ("hello", "No", False),
            ("level", "Yes", True),
        ],
    },
    {
        "title": "Count Vowels in a String",
        "topic": "Strings",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read a string S (lowercase letters) and print the number of vowels (a, e, i, o, u) it contains.",
        "hint": "Loop through the string and check membership in the set 'aeiou'.",
        "answer": "s = input()\nprint(sum(1 for ch in s if ch in 'aeiou'))",
        "sample_input": "programming",
        "sample_output": "3",
        "time_limit": 15,
        "test_cases": [
            ("programming", "3", False),
            ("rhythm", "0", False),
            ("education", "5", True),
        ],
    },
    {
        "title": "GCD of Two Numbers",
        "topic": "Math",
        "difficulty": "Easy",
        "language": "python",
        "description": "Read two positive integers A and B and print their Greatest Common Divisor (GCD) using the Euclidean algorithm.",
        "hint": "Repeatedly replace (a, b) with (b, a % b) until b becomes 0.",
        "answer": "a = int(input())\nb = int(input())\nwhile b:\n    a, b = b, a % b\nprint(a)",
        "sample_input": "12\n18",
        "sample_output": "6",
        "time_limit": 20,
        "test_cases": [
            ("12\n18", "6", False),
            ("17\n5", "1", False),
            ("100\n75", "25", True),
        ],
    },

    # ------------------------- MEDIUM (3) -------------------------
    {
        "title": "Find the Missing Number",
        "topic": "Arrays",
        "difficulty": "Medium",
        "language": "python",
        "description": (
            "An array contains N distinct integers taken from the range 1 to N+1, "
            "with exactly one number missing. Given N followed by the N numbers, "
            "print the missing number."
        ),
        "hint": "Sum of 1..N+1 minus the sum of the given array gives the missing number.",
        "answer": (
            "n = int(input())\n"
            "nums = [int(input()) for _ in range(n)]\n"
            "expected = (n + 1) * (n + 2) // 2\n"
            "print(expected - sum(nums))"
        ),
        "sample_input": "4\n1\n2\n4\n5",
        "sample_output": "3",
        "time_limit": 25,
        "test_cases": [
            ("4\n1\n2\n4\n5", "3", False),
            ("3\n1\n2\n3", "4", False),
            ("1\n2", "1", True),
        ],
    },
    {
        "title": "Prime Numbers up to N",
        "topic": "Math",
        "difficulty": "Medium",
        "language": "python",
        "description": (
            "Read an integer N and print all prime numbers from 2 to N (inclusive), "
            "space-separated, on a single line."
        ),
        "hint": "Use the Sieve of Eratosthenes for efficiency.",
        "answer": (
            "n = int(input())\n"
            "sieve = [True] * (n + 1)\n"
            "sieve[0:2] = [False, False]\n"
            "for i in range(2, int(n ** 0.5) + 1):\n"
            "    if sieve[i]:\n"
            "        for j in range(i * i, n + 1, i):\n"
            "            sieve[j] = False\n"
            "print(' '.join(str(i) for i in range(n + 1) if sieve[i]))"
        ),
        "sample_input": "20",
        "sample_output": "2 3 5 7 11 13 17 19",
        "time_limit": 25,
        "test_cases": [
            ("20", "2 3 5 7 11 13 17 19", False),
            ("10", "2 3 5 7", False),
            ("2", "2", True),
        ],
    },
    {
        "title": "Cricket Fastest Fifty",
        "topic": "Arrays",
        "difficulty": "Medium",
        "language": "python",
        "description": (
            "In a cricket match, N batsmen each scored a fifty (50+ runs). Given N, "
            "followed by N pairs of (runs, balls_faced), find and print the runs and "
            "balls faced of the batsman who reached their fifty in the FEWEST balls "
            "(i.e., the smallest balls_faced value), in the format 'runs balls'. "
            "If there is a tie, print the one that appears first in the input."
        ),
        "hint": "Track the minimum balls_faced while scanning the list once.",
        "answer": (
            "n = int(input())\n"
            "best = None\n"
            "for _ in range(n):\n"
            "    runs, balls = map(int, input().split())\n"
            "    if best is None or balls < best[1]:\n"
            "        best = (runs, balls)\n"
            "print(f'{best[0]} {best[1]}')"
        ),
        "sample_input": "3\n55 40\n62 28\n50 35",
        "sample_output": "62 28",
        "time_limit": 25,
        "test_cases": [
            ("3\n55 40\n62 28\n50 35", "62 28", False),
            ("2\n50 30\n70 30", "50 30", False),
            ("1\n99 45", "99 45", True),
        ],
    },

    # ------------------------- HARD (5) -------------------------
    {
        "title": "Longest Common Subsequence",
        "topic": "Dynamic Programming",
        "difficulty": "Hard",
        "language": "python",
        "description": (
            "Given two strings S1 and S2 (one per line), print the length of their "
            "Longest Common Subsequence (LCS)."
        ),
        "hint": "Build a 2D DP table where dp[i][j] is the LCS length of S1[:i] and S2[:j].",
        "answer": (
            "s1 = input()\n"
            "s2 = input()\n"
            "m, n = len(s1), len(s2)\n"
            "dp = [[0] * (n + 1) for _ in range(m + 1)]\n"
            "for i in range(1, m + 1):\n"
            "    for j in range(1, n + 1):\n"
            "        if s1[i - 1] == s2[j - 1]:\n"
            "            dp[i][j] = dp[i - 1][j - 1] + 1\n"
            "        else:\n"
            "            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])\n"
            "print(dp[m][n])"
        ),
        "sample_input": "abcde\nace",
        "sample_output": "3",
        "time_limit": 40,
        "test_cases": [
            ("abcde\nace", "3", False),
            ("abc\nabc", "3", False),
            ("abc\ndef", "0", True),
        ],
    },
    {
        "title": "Merge Overlapping Intervals",
        "topic": "Arrays",
        "difficulty": "Hard",
        "language": "python",
        "description": (
            "Given N intervals, each as 'start end' on its own line, merge all "
            "overlapping intervals and print the merged intervals sorted by start, "
            "one per line, in the format 'start end'."
        ),
        "hint": "Sort intervals by start time, then sweep through merging when the current start <= previous end.",
        "answer": (
            "n = int(input())\n"
            "intervals = [tuple(map(int, input().split())) for _ in range(n)]\n"
            "intervals.sort()\n"
            "merged = []\n"
            "for start, end in intervals:\n"
            "    if merged and start <= merged[-1][1]:\n"
            "        merged[-1] = (merged[-1][0], max(merged[-1][1], end))\n"
            "    else:\n"
            "        merged.append((start, end))\n"
            "for s, e in merged:\n"
            "    print(s, e)"
        ),
        "sample_input": "4\n1 3\n2 6\n8 10\n15 18",
        "sample_output": "1 6\n8 10\n15 18",
        "time_limit": 40,
        "test_cases": [
            ("4\n1 3\n2 6\n8 10\n15 18", "1 6\n8 10\n15 18", False),
            ("2\n1 4\n4 5", "1 5", False),
            ("1\n1 2", "1 2", True),
        ],
    },
    {
        "title": "Kth Largest Element",
        "topic": "Arrays",
        "difficulty": "Hard",
        "language": "python",
        "description": (
            "Given an array of N integers and an integer K, print the Kth largest "
            "element in the array (1-indexed, i.e., K=1 means the largest element)."
        ),
        "hint": "Sort the array in descending order and pick index K-1, or use a min-heap of size K.",
        "answer": (
            "n = int(input())\n"
            "nums = [int(input()) for _ in range(n)]\n"
            "k = int(input())\n"
            "nums.sort(reverse=True)\n"
            "print(nums[k - 1])"
        ),
        "sample_input": "6\n3\n2\n1\n5\n6\n4\n2",
        "sample_output": "5",
        "time_limit": 35,
        "test_cases": [
            ("6\n3\n2\n1\n5\n6\n4\n2", "5", False),
            ("4\n8\n1\n2\n9\n1", "8", False),
            ("3\n7\n7\n7\n2", "7", True),
        ],
    },
    {
        "title": "Minimum Coins for Change",
        "topic": "Dynamic Programming",
        "difficulty": "Hard",
        "language": "python",
        "description": (
            "Given N distinct coin denominations followed by a target amount, print "
            "the minimum number of coins needed to make that exact amount. If it is "
            "not possible, print -1."
        ),
        "hint": "Classic unbounded-knapsack style DP: dp[amount] = min coins to make 'amount'.",
        "answer": (
            "n = int(input())\n"
            "coins = [int(input()) for _ in range(n)]\n"
            "amount = int(input())\n"
            "INF = float('inf')\n"
            "dp = [0] + [INF] * amount\n"
            "for a in range(1, amount + 1):\n"
            "    for c in coins:\n"
            "        if c <= a and dp[a - c] + 1 < dp[a]:\n"
            "            dp[a] = dp[a - c] + 1\n"
            "print(dp[amount] if dp[amount] != INF else -1)"
        ),
        "sample_input": "3\n1\n2\n5\n11",
        "sample_output": "3",
        "time_limit": 40,
        "test_cases": [
            ("3\n1\n2\n5\n11", "3", False),
            ("1\n2\n3", "-1", False),
            ("2\n1\n5\n0", "0", True),
        ],
    },
    {
        "title": "Longest Palindromic Substring",
        "topic": "Strings",
        "difficulty": "Hard",
        "language": "python",
        "description": (
            "Given a string S, print the longest palindromic substring of S. If "
            "there are multiple with the same length, print the one that starts "
            "first."
        ),
        "hint": "Expand around every possible center (both odd and even length palindromes).",
        "answer": (
            "s = input()\n"
            "def expand(l, r):\n"
            "    while l >= 0 and r < len(s) and s[l] == s[r]:\n"
            "        l -= 1\n"
            "        r += 1\n"
            "    return s[l + 1:r]\n"
            "best = ''\n"
            "for i in range(len(s)):\n"
            "    for cand in (expand(i, i), expand(i, i + 1)):\n"
            "        if len(cand) > len(best):\n"
            "            best = cand\n"
            "print(best)"
        ),
        "sample_input": "babad",
        "sample_output": "bab",
        "time_limit": 40,
        "test_cases": [
            ("babad", "bab", False),
            ("cbbd", "bb", False),
            ("a", "a", True),
        ],
    },
]

DIFFICULTY_MAP_ASSESSMENT = {"Easy": "easy", "Medium": "medium", "Hard": "hard"}


class Command(BaseCommand):
    help = "Seed 16 questions (8 Easy / 3 Medium / 5 Hard) into the practice bank and a new Assessment. Safe to re-run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--assessment-title",
            type=str,
            default="Practice Set - Fundamentals (16 Qs)",
            help="Title of the Assessment these questions will be attached to.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        created_practice = 0
        skipped_practice = 0
        created_assessment_q = 0
        skipped_assessment_q = 0

        # ---- 1. Practice bank (questions app) ----
        for q in QUESTIONS:
            obj, created = PracticeQuestion.objects.get_or_create(
                title=q["title"],
                defaults={
                    "description": q["description"],
                    "topic": q["topic"],
                    "difficulty": q["difficulty"],
                    "sample_input": q["sample_input"],
                    "sample_output": q["sample_output"],
                    "hint": q["hint"],
                    "answer": q["answer"],
                    "time_limit": q["time_limit"],
                },
            )
            if created:
                created_practice += 1
                for input_data, expected_output, is_hidden in q["test_cases"]:
                    PracticeTestCase.objects.get_or_create(
                        question=obj,
                        input_data=input_data,
                        expected_output=expected_output,
                        defaults={"is_hidden": is_hidden},
                    )
                self.stdout.write(self.style.SUCCESS(f"[practice] created: {q['title']}"))
            else:
                skipped_practice += 1
                self.stdout.write(self.style.WARNING(f"[practice] already exists, skipped: {q['title']}"))

        # ---- 2. Assessment (assessments app) ----
        assessment_title = options["assessment_title"]
        assessment, _ = Assessment.objects.get_or_create(
            title=assessment_title,
            defaults={"duration": 90, "total_marks": 100, "difficulty": "Intermediate"},
        )

        for q in QUESTIONS:
            obj, created = AssessmentQuestion.objects.get_or_create(
                assessment=assessment,
                title=q["title"],
                defaults={
                    "text": q["description"],
                    "problem_statement": q["description"],
                    "difficulty": DIFFICULTY_MAP_ASSESSMENT[q["difficulty"]],
                    "question_type": "coding",
                    "language": q["language"],
                    "hint": q["hint"],
                    "solution": q["answer"],
                    "time_limit": q["time_limit"],
                },
            )
            if created:
                created_assessment_q += 1
                for order, (input_data, expected_output, is_hidden) in enumerate(q["test_cases"]):
                    AssessmentTestCase.objects.get_or_create(
                        question=obj,
                        input_data=input_data,
                        expected_output=expected_output,
                        defaults={"is_sample": not is_hidden, "order": order},
                    )
                self.stdout.write(self.style.SUCCESS(f"[assessment] created: {q['title']}"))
            else:
                skipped_assessment_q += 1
                self.stdout.write(self.style.WARNING(f"[assessment] already exists, skipped: {q['title']}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Practice bank: {created_practice} created, {skipped_practice} skipped. "
            f"Assessment '{assessment_title}': {created_assessment_q} created, {skipped_assessment_q} skipped."
        ))
