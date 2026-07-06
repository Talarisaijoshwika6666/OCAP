import django.db.models.deletion
from django.db import migrations, models
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('assessments', '0002_question_marks'),
        ('results', '0001_initial'),
    ]
 
    operations = [
        migrations.AddField(
            model_name='result',
            name='total_questions',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='correct_answers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='wrong_answers',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='total_marks',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='percentage',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='result',
            name='passed',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='CandidateAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_option', models.CharField(blank=True, max_length=1, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=20, null=True)),
                ('test_cases_passed', models.PositiveIntegerField(default=0)),
                ('total_test_cases', models.PositiveIntegerField(default=0)),
                ('is_correct', models.BooleanField(default=False)),
                ('marks_awarded', models.FloatField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidate_answers', to='assessments.question')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='results.result')),
            ],
            options={
                'ordering': ['question__id'],
            },
        ),
    ]
 
