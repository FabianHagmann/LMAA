# Generated by Django 4.1.7 on 2023-03-20 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='default',
            field=models.CharField(default='', max_length=64),
        ),
    ]
