# Generated by Django 4.1.7 on 2023-03-30 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0006_testcase_assignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='containstestcase',
            name='testcase_ptr',
        ),
        migrations.RemoveField(
            model_name='testcase',
            name='assignment',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='solution',
        ),
        migrations.RemoveField(
            model_name='testresult',
            name='testcase',
        ),
        migrations.RemoveField(
            model_name='unittestcase',
            name='testcase_ptr',
        ),
        migrations.RemoveField(
            model_name='solution',
            name='testresults',
        ),
        migrations.DeleteModel(
            name='CompilesTestcase',
        ),
        migrations.DeleteModel(
            name='ContainsTestcase',
        ),
        migrations.DeleteModel(
            name='Testcase',
        ),
        migrations.DeleteModel(
            name='Testresult',
        ),
        migrations.DeleteModel(
            name='UnitTestcase',
        ),
    ]
