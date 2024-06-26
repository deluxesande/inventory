# Generated by Django 5.0.6 on 2024-06-05 13:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_reports_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingReports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updates_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('description', models.CharField(max_length=200, null=True)),
                ('receipts', models.CharField(max_length=200, null=True)),
                ('payments', models.CharField(max_length=200, null=True)),
                ('for_edit', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('category', models.ManyToManyField(to='dashboard.maincategory')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
