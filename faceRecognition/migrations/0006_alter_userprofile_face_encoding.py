# Generated by Django 5.0.4 on 2024-08-26 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faceRecognition', '0005_alter_userprofile_face_encoding'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='face_encoding',
            field=models.BinaryField(blank=True),
        ),
    ]
