# Generated by Django 3.0.8 on 2020-07-27 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0004_auto_20200724_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='timestamp',
            field=models.DateField(auto_now_add=True),
        ),
    ]