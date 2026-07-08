from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_question_time_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='constraints',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='question',
            name='input_format',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='question',
            name='output_format',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='question',
            name='memory_limit_mb',
            field=models.PositiveIntegerField(default=256, help_text='Memory limit in MB for this question'),
        ),
        migrations.AddField(
            model_name='question',
            name='marks',
            field=models.PositiveIntegerField(default=0, help_text='Marks this question is worth in a contest (0 = untracked / Problem Bank question)'),
        ),
    ]
