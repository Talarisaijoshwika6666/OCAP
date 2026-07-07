from django import forms
from questions.models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'title', 'description', 'topic', 'difficulty',
            'sample_input', 'sample_output', 'hint', 'answer', 'time_limit',
        ]
        widgets = {
            'title':          forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Problem title'}),
            'description':    forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Full problem statement...'}),
            'topic':          forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Arrays, Recursion'}),
            'difficulty':     forms.Select(attrs={'class': 'form-input'}),
            'sample_input':   forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional sample input'}),
            'sample_output':  forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional sample output'}),
            'hint':           forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional hint shown to candidates'}),
            'answer':         forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Optional reference solution'}),
            'time_limit':     forms.NumberInput(attrs={'class': 'form-input'}),
        }
