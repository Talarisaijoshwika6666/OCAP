from django import forms
from assessments.models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'assessment',
            'title',
            'problem_statement',
            'difficulty',
            'question_type',
            'language',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'hint',
            'solution',
        ]