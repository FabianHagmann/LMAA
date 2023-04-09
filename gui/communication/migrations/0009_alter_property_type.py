# Generated by Django 4.1.7 on 2023-03-30 14:14

from django.db import migrations, models
import gui.communication.models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0008_alter_solutionrequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='type',
            field=models.IntegerField(choices=[(1, 'int'), (2, 'float'), (3, 'str'), (4, 'select')], default=gui.communication.models.PropertyType['float']),
        ),
    ]