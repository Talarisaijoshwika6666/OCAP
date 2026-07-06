from assessments.models import Assessment, Question

def ensure_assessments_exist():
    if Assessment.objects.count() == 0:
        a1 = Assessment.objects.create(
            title="Frontend Engineer Core Assessment", 
            duration=45, 
            total_marks=100, 
            difficulty="Intermediate", 
            is_active=True
        )
        Question.objects.create(
            assessment=a1,
            text="What is the correct HTML element for inserting a line break?",
            correct_option="C",
            option_a="<lb>",
            option_b="<break>",
            option_c="<br>",
            option_d="<newline>",
            difficulty="easy",
            question_type="mcq",
            marks=50
        )
        Question.objects.create(
            assessment=a1,
            text="Which CSS property controls the text size?",
            correct_option="A",
            option_a="font-size",
            option_b="text-style",
            option_c="font-style",
            option_d="text-size",
            difficulty="easy",
            question_type="mcq",
            marks=50
        )

        a2 = Assessment.objects.create(
            title="Python & Algorithms Test #2", 
            duration=60, 
            total_marks=150, 
            difficulty="Advanced", 
            is_active=True
        )
        Question.objects.create(
            assessment=a2,
            text="What is the correct syntax to output the type of a variable in Python?",
            correct_option="B",
            option_a="print(typeof(x))",
            option_b="print(type(x))",
            option_c="print(typeOf(x))",
            option_d="print(typeof x)",
            difficulty="medium",
            question_type="mcq",
            marks=75
        )
        Question.objects.create(
            assessment=a2,
            text="Which of the following is not a built-in collection type in Python?",
            correct_option="D",
            option_a="List",
            option_b="Tuple",
            option_c="Set",
            option_d="Array",
            difficulty="medium",
            question_type="mcq",
            marks=75
        )

        a3 = Assessment.objects.create(
            title="Database & SQL Skills Assessment", 
            duration=30, 
            total_marks=80, 
            difficulty="Beginner", 
            is_active=True
        )
        Question.objects.create(
            assessment=a3,
            text="Which SQL statement is used to extract data from a database?",
            correct_option="D",
            option_a="OPEN",
            option_b="GET",
            option_c="EXTRACT",
            option_d="SELECT",
            difficulty="easy",
            question_type="mcq",
            marks=40
        )
        Question.objects.create(
            assessment=a3,
            text="Which SQL statement is used to update data in a database?",
            correct_option="B",
            option_a="SAVE",
            option_b="UPDATE",
            option_c="MODIFY",
            option_d="SAVE AS",
            difficulty="easy",
            question_type="mcq",
            marks=40
        )
