# Generated by Django 5.1.3 on 2024-12-04 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_posting_schedule_posting_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='common_promotional_message',
            field=models.TextField(default='', max_length=2024),
        ),
        migrations.AddField(
            model_name='blog',
            name='common_prompt',
            field=models.TextField(default='', max_length=2024),
        ),
    ]
