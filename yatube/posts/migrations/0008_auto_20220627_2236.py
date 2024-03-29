# Generated by Django 2.2.16 on 2022-06-27 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20220625_0948'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(
                fields=('user', 'author'),
                name='follow_user_author_unique_relationships'
            ),
        ),
    ]
