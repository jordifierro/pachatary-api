# Generated by Django 2.1.3 on 2018-11-14 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_removeusername'),
    ]

    operations = [
        migrations.CreateModel(
            name='ORMBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_person', to='people.ORMPerson')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_person', to='people.ORMPerson')),
            ],
            options={
                'verbose_name': 'Block',
                'verbose_name_plural': 'Blocks',
            },
        ),
    ]
