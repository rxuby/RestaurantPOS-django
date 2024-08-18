# Generated by Django 4.1.7 on 2023-03-23 19:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posApp', '0015_material_added_stock_alter_sales_tablename'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='material',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
