# Generated by Django 2.0.7 on 2018-07-03 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0003_ormexperience_share_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormexperience',
            name='share_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]