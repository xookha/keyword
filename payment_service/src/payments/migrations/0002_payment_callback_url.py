# Generated by Django 2.2 on 2019-04-20 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='callback_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]