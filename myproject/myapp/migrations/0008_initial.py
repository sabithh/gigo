# Generated by Django 5.1.5 on 2025-01-18 12:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('myapp', '0007_remove_jobs_booked_by_remove_jobs_owner_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15, null=True, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='owner_photos/')),
                ('location', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('age', models.PositiveIntegerField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1, null=True)),
                ('password', models.CharField(max_length=128)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='user_photos/')),
                ('bio', models.TextField(blank=True, null=True)),
                ('place', models.CharField(blank=True, max_length=100, null=True)),
                ('rating', models.FloatField(blank=True, default=0.0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('available_slot', models.IntegerField()),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('D', 'Declined')], default='P', max_length=1)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='myapp.owners')),
                ('booked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bookings', to='myapp.usermodel')),
            ],
        ),
    ]
