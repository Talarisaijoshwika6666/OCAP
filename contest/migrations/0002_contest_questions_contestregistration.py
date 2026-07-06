from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('questions', '0006_question_time_limit'),
        ('contest', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
 
    operations = [
        migrations.AlterModelOptions(
            name='contest',
            options={'ordering': ['-start_time']},
        ),
        migrations.AddField(
            model_name='contest',
            name='questions',
            field=models.ManyToManyField(blank=True, related_name='contests', to='questions.question'),
        ),
        migrations.CreateModel(
            name='ContestRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='contest.contest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contest_registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('contest', 'user')},
            },
        ),
    ]
