# Generated by Django 4.2 on 2023-04-17 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0007_remove_containstestcase_testcase_ptr_and_more'),
        ('testing', '0003_testresult_message'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Testresult',
            new_name='CompilesTestresult',
        ),
        migrations.RemoveField(
            model_name='testcase',
            name='testresults',
        ),
        migrations.AddField(
            model_name='compilestestcase',
            name='testresults',
            field=models.ManyToManyField(through='testing.CompilesTestresult', to='assignments.solution'),
        ),
        migrations.AlterField(
            model_name='compilestestresult',
            name='testcase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testing.compilestestcase'),
        ),
        migrations.AlterModelTable(
            name='compilestestresult',
            table='compiles_testresult',
        ),
        migrations.CreateModel(
            name='UnitTestresult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True)),
                ('result', models.BooleanField(blank=True)),
                ('total_testcases', models.PositiveIntegerField()),
                ('success_testcases', models.PositiveIntegerField()),
                ('message', models.CharField(default=' ', max_length=8196)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments.solution')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testing.unittestcase')),
            ],
            options={
                'db_table': 'unit_testresult',
            },
        ),
        migrations.CreateModel(
            name='ContainsTestresult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True)),
                ('result', models.BooleanField(blank=True)),
                ('count_wanted', models.PositiveIntegerField(blank=True)),
                ('count_found', models.PositiveIntegerField(blank=True)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments.solution')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testing.containstestcase')),
            ],
            options={
                'db_table': 'contains_testresult',
            },
        ),
        migrations.AddField(
            model_name='containstestcase',
            name='testresults',
            field=models.ManyToManyField(through='testing.ContainsTestresult', to='assignments.solution'),
        ),
        migrations.AddField(
            model_name='unittestcase',
            name='testresults',
            field=models.ManyToManyField(through='testing.UnitTestresult', to='assignments.solution'),
        ),
    ]