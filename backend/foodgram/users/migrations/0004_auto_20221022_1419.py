# Generated by Django 2.2.16 on 2022-10-22 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20221022_1411'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='self_following',
        ),
    ]
