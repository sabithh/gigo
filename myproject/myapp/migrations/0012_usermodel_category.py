# Generated by Django 5.1.5 on 2025-01-22 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_owners_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
