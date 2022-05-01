# Generated by Django 4.0.4 on 2022-05-01 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('M', 'Moving Forward'), ('R', 'Rejected')], default='P', max_length=1),
        ),
    ]
