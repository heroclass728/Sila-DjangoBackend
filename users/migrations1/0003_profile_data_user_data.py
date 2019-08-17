# Generated by Django 2.2.4 on 2019-08-10 23:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_custom_verification_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='user_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.IntegerField()),
                ('name', models.CharField(max_length=40)),
                ('age', models.IntegerField(null=True)),
                ('email', models.EmailField(blank=True, max_length=70, null=True, unique=True)),
                ('gender', models.CharField(max_length=10)),
                ('account_key', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='profile_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription', models.IntegerField(default=0)),
                ('reports', models.IntegerField(default=0)),
                ('account_key', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
