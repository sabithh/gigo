# Generated by Django 5.1.5 on 2025-01-18 10:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_owners_jobs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobs',
            name='owner',
        ),
        migrations.AddField(
            model_name='jobs',
            name='booked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.usermodel'),
        ),
    ]
