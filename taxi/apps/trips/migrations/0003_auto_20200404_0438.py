# Generated by Django 2.2.8 on 2020-04-04 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trips', '0002_trip'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trip',
            old_name='update',
            new_name='updated',
        ),
    ]
