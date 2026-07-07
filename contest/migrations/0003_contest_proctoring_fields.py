from django.db import migrations, models
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('contest', '0002_contest_questions_contestregistration'),
    ]
 
    operations = [
        migrations.AddField(
            model_name='contestregistration',
            name='violation_count',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Number of tab-switch / focus-loss violations recorded during this contest.',
            ),
        ),
        migrations.AddField(
            model_name='contestregistration',
            name='auto_submitted',
            field=models.BooleanField(
                default=False,
                help_text='True once the test was force-submitted due to repeated proctoring violations.',
            ),
        ),
        migrations.AddField(
            model_name='contestregistration',
            name='auto_submitted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
 
