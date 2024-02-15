# Generated by Django 4.2.7 on 2024-02-08 07:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0034_rename_date_feestructure_starting_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_assignment', models.CharField(blank=True, choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2')], default='Not-Set', max_length=50, null=True)),
                ('starting_date', models.DateField(default=django.utils.timezone.now)),
                ('months_range', models.CharField(blank=True, max_length=50, null=True)),
                ('invoice_number', models.CharField(max_length=12)),
                ('total_amount_to_pay', models.IntegerField()),
                ('candidate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crmpage.candidate')),
            ],
        ),
    ]
