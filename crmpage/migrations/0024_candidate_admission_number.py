# Generated by Django 4.2.7 on 2024-01-12 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0023_alter_invoice_invoice_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='admission_number',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
