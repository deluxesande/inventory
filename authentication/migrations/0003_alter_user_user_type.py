# Generated by Django 5.0.6 on 2024-06-05 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('accountant', 'Accountant'), ('manager', 'Manager')], default='manager', max_length=20),
        ),
    ]
