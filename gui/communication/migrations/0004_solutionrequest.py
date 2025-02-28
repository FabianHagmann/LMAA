# Generated by Django 4.1.7 on 2023-03-21 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0004_alter_tag_name'),
        ('communication', '0003_property_is_configuration'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolutionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('assignments', models.ManyToManyField(to='assignments.assignment')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communication.languagemodel')),
            ],
            options={
                'db_table': 'solution_request',
            },
        ),
    ]
