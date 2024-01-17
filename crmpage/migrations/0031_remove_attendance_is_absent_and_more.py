# Generated by Django 4.2.7 on 2024-01-15 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0030_remove_attendance_absent_remove_attendance_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='is_absent',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='is_late',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='is_present',
        ),
        migrations.AddField(
            model_name='attendance',
            name='absent',
            field=models.CharField(choices=[('present', 'Present'), ('absent_with_reason', 'Absent with Reason'), ('late', 'Late'), ('absent_without_reason', 'Absent without Reason')], default='present', max_length=50, null=True),
        ),
    ]
