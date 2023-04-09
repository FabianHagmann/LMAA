# Generated by Django 4.1.7 on 2023-03-30 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('assignments', '0007_remove_containstestcase_testcase_ptr_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testcase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments.assignment')),
            ],
            options={
                'db_table': 'testcase',
            },
        ),
        migrations.CreateModel(
            name='CompilesTestcase',
            fields=[
                ('testcase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='testing.testcase')),
                ('active', models.BooleanField(blank=True)),
            ],
            options={
                'db_table': 'compiles_testcase',
            },
            bases=('testing.testcase',),
        ),
        migrations.CreateModel(
            name='ContainsTestcase',
            fields=[
                ('testcase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='testing.testcase')),
                ('phrase', models.CharField(max_length=64)),
                ('times', models.IntegerField(blank=True, default=1)),
            ],
            options={
                'db_table': 'contains_testcase',
            },
            bases=('testing.testcase',),
        ),
        migrations.CreateModel(
            name='UnitTestcase',
            fields=[
                ('testcase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='testing.testcase')),
                ('file', models.FileField(blank=True, upload_to='db_files/')),
            ],
            options={
                'db_table': 'unit_testcase',
            },
            bases=('testing.testcase',),
        ),
        migrations.CreateModel(
            name='Testresult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True)),
                ('result', models.BooleanField(blank=True)),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments.solution')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testing.testcase')),
            ],
            options={
                'db_table': 'testresult',
            },
        ),
        migrations.AddField(
            model_name='testcase',
            name='testresults',
            field=models.ManyToManyField(through='testing.Testresult', to='assignments.solution'),
        ),
    ]