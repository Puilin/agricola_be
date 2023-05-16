# Generated by Django 4.2.1 on 2023-05-16 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('email', models.CharField(default='-', max_length=30, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=10)),
                ('user_id', models.CharField(max_length=20, unique=True)),
                ('user_pw', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='BoardPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField()),
                ('position_name', models.CharField(default='빈칸', max_length=6)),
                ('is_fam', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cardname', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('filename', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adult_num', models.IntegerField(default=2)),
                ('baby_num', models.IntegerField(default=0)),
                ('fst_player', models.BooleanField(default=False)),
                ('score', models.IntegerField(default=0)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.account')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_name', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='SubFacilityCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.card')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.file')),
                ('resource_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.resource')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_num', models.IntegerField(default=0)),
                ('player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.player')),
                ('resource_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.resource')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerBoardStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house', models.CharField(default='나무', max_length=2)),
                ('room_num', models.IntegerField(default=2)),
                ('player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.player')),
            ],
        ),
        migrations.CreateModel(
            name='PeriodCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField()),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.card')),
            ],
        ),
        migrations.CreateModel(
            name='MainFacilityCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.card')),
            ],
        ),
        migrations.CreateModel(
            name='JobCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.card')),
            ],
        ),
        migrations.CreateModel(
            name='FencePosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('left', models.BooleanField(default=False)),
                ('top', models.BooleanField(default=False)),
                ('right', models.BooleanField(default=False)),
                ('bottom', models.BooleanField(default=False)),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.boardposition')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='card_img',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.file'),
        ),
        migrations.AddField(
            model_name='boardposition',
            name='board_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.playerboardstatus'),
        ),
        migrations.CreateModel(
            name='ActivationCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_num', models.IntegerField()),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.card')),
                ('resource_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.resource')),
            ],
        ),
        migrations.CreateModel(
            name='ActionBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acc_resource', models.IntegerField(default=0)),
                ('add_resource', models.IntegerField(default=0)),
                ('round', models.IntegerField()),
                ('card_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameplay.periodcard')),
            ],
        ),
    ]
