# Generated by Django 4.2.7 on 2023-12-15 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmpage', '0006_alter_candidate_qualification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='Course_Location',
            field=models.CharField(choices=[('Mombasa', 'Mombasa (001)'), ('Kwale', 'Kwale (002 )'), ('Kilifi', 'Kilifi (003)'), ('Tana River', 'Tana River (004)'), ('Lamu', 'Lamu (005)'), ('Taita–Taveta', 'Taita–Taveta (006)'), ('Garissa', 'Garissa (007)'), ('Wajir', 'Wajir (008)'), ('Mandera', 'Mandera (009)'), ('Marsabit', 'Marsabit (010)'), ('Isiolo', 'Isiolo (011)'), ('Meru', 'Meru (012)'), ('Tharaka-Nithi', 'Tharaka-Nithi (013)'), ('Embu', 'Embu (014)'), ('Kitui', 'Kitui (015)'), ('Makueni', 'Makueni (017)'), ('Nyandarua', 'Nyandarua (018)'), ('Nyeri', 'Nyeri (019)'), ('Kirinyaga', 'Kirinyaga (020)'), ('Muranga', 'Muranga (021)'), ('Kiambu', 'Kiambu (022)'), ('Turkana', 'Turkana (023)'), ('West Pokot', 'West Pokot (024)'), ('Samburu', 'Samburu (025)'), ('Trans-Nzoia', 'Trans-Nzoia (026)'), ('Uasin Gishu', 'Uasin Gishu (027)'), ('Elgeyo-Marakwet', 'Elgeyo-Marakwet (028)'), ('Nandi Kapsabet', 'Nandi Kapsabet (029)'), ('Baringo Kabarnet', 'Baringo Kabarnet (030)'), ('Laikipia', 'Laikipia (031)'), ('Nakuru', 'Nakuru (032)'), ('Narok', 'Narok (033)'), ('Kajiado', 'Kajiado (034)'), ('Kericho', 'Kericho (035)'), ('Bomet', 'Bomet (036)'), ('Kakamega', 'Kakamega (037)'), ('Vihiga', 'Vihiga (038)'), ('Bungoma', 'Bungoma (039)'), ('Busia', 'Busia (040)'), ('Siaya', 'Siaya (041)'), ('Kisumu', 'Kisumu (042)'), ('Homa Bay', 'Homa Bay (043)'), ('Migori', 'Migori (044)'), ('Kisii', 'Kisii (045)'), ('Nyamira', 'Nyamira (046)'), ('Nairobi', 'Nairobi (047)')], max_length=50, null=True),
        ),
    ]