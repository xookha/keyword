# Generated by Django 2.1.7 on 2019-03-25 21:31

from django.db import migrations, models
import keywords.models


class Migration(migrations.Migration):

    dependencies = [
        ('keywords', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='url',
            field=models.URLField(validators=[keywords.models.check_url]),
        ),
    ]