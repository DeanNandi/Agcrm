# Generated by Django 4.2.7 on 2023-12-14 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0003_remove_candidate_course_class_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='candidate_photos/'),
        ),
    ]
