# Generated by Django 5.1.5 on 2025-02-26 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vibes', '0004_event_poster_alter_event_name_alter_event_venue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='event',
            name='venue',
            field=models.CharField(max_length=200),
        ),
    ]
