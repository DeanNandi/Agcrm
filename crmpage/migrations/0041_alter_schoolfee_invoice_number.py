# Generated by Django 4.2.7 on 2024-02-08 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0040_schoolfee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolfee',
            name='invoice_number',
            field=models.CharField(max_length=12),
        ),
    ]