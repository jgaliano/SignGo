# Generated by Django 5.0.6 on 2024-10-03 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eSignAnyWhere', '0003_alter_documentos_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmante',
            name='sobre',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='firmante',
            name='tipo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
