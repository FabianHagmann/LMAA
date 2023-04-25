# Generated by Django 4.2 on 2023-04-23 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0004_rename_testresult_compilestestresult_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containstestresult',
            name='count_found',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='containstestresult',
            name='count_wanted',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='unittestresult',
            name='success_testcases',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='unittestresult',
            name='total_testcases',
            field=models.IntegerField(),
        ),
    ]