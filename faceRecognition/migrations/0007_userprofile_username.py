# Generated by Django 5.0.4 on 2024-08-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceRecognition', '0006_alter_userprofile_face_encoding'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(default='default_user', max_length=150, unique=True),
        ),
    ]
