from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0005_bookmark'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.CharField(blank=True, default='General', max_length=100),
        ),
    ]
