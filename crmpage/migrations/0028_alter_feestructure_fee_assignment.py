# Generated by Django 4.2.7 on 2024-02-06 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0027_feestructure_fee_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feestructure',
            name='fee_assignment',
            field=models.CharField(blank=True, choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2')], default='Not-Set', max_length=50, null=True),
        ),
    ]
