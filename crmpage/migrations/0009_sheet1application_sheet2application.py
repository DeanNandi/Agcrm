# Generated by Django 4.2.7 on 2023-12-21 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0008_application_sheet_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sheet1Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('age', models.CharField(blank=True, max_length=255, null=True)),
                ('qualification', models.TextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('level_of_german', models.CharField(blank=True, max_length=255, null=True)),
                ('enrol_in_course', models.CharField(blank=True, max_length=255, null=True)),
                ('questions', models.CharField(blank=True, max_length=255, null=True)),
                ('time_for_class', models.CharField(blank=True, max_length=255, null=True)),
                ('online_or_physical', models.CharField(blank=True, max_length=255, null=True)),
                ('days_for_class', models.CharField(blank=True, max_length=255, null=True)),
                ('license_number', models.CharField(blank=True, max_length=255, null=True)),
                ('Reply', models.CharField(choices=[('Pending', 'Pending'), ('Eligible', 'Eligible'), ('Not-Eligible', 'Not-Eligible'), ('Not-Now', 'Not-Now')], default='Pending', max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sheet2Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('age', models.CharField(blank=True, max_length=255, null=True)),
                ('qualification', models.TextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('level_of_german', models.CharField(blank=True, max_length=255, null=True)),
                ('enrol_in_course', models.CharField(blank=True, max_length=255, null=True)),
                ('questions', models.CharField(blank=True, max_length=255, null=True)),
                ('time_for_class', models.CharField(blank=True, max_length=255, null=True)),
                ('online_or_physical', models.CharField(blank=True, max_length=255, null=True)),
                ('days_for_class', models.CharField(blank=True, max_length=255, null=True)),
                ('license_number', models.CharField(blank=True, max_length=255, null=True)),
                ('Reply', models.CharField(choices=[('Pending', 'Pending'), ('Eligible', 'Eligible'), ('Not-Eligible', 'Not-Eligible'), ('Not-Now', 'Not-Now')], default='Pending', max_length=50, null=True)),
            ],
        ),
    ]