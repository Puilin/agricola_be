# Generated by Django 4.2.1 on 2023-06-05 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0002_rename_player_id_boardposition_board_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerboardstatus',
            name='fence_num',
            field=models.IntegerField(default=0),
        ),
    ]
