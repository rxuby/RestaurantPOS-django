# Generated by Django 4.1.7 on 2023-03-19 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posApp', '0003_alter_customuser_salary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
