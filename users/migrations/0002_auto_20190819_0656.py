# Generated by Django 2.1.8 on 2019-08-19 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_data',
            name='account_key',
        ),
        migrations.AddField(
            model_name='user_data',
            name='account_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
