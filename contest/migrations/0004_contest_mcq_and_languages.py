import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contest', '0003_contest_proctoring_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='topic',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='contest',
            name='allowed_languages',
            field=models.CharField(
                blank=True,
                default='python,cpp,java,javascript',
                help_text='Comma-separated language codes candidates may use (see LANGUAGE_CHOICES).',
                max_length=200,
            ),
        ),
        migrations.CreateModel(
            name='ContestMCQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('option_a', models.CharField(max_length=500)),
                ('option_b', models.CharField(max_length=500)),
                ('option_c', models.CharField(max_length=500)),
                ('option_d', models.CharField(max_length=500)),
                ('correct_option', models.CharField(choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')], max_length=1)),
                ('difficulty', models.CharField(choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default='Easy', max_length=10)),
                ('marks', models.PositiveIntegerField(default=1)),
                ('order', models.PositiveIntegerField(default=0)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mcqs', to='contest.contest')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ContestMCQAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_option', models.CharField(choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')], max_length=1)),
                ('is_correct', models.BooleanField(default=False)),
                ('answered_at', models.DateTimeField(auto_now=True)),
                ('mcq', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='contest.contestmcq')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contest_mcq_answers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('mcq', 'user')},
            },
        ),
    ]
