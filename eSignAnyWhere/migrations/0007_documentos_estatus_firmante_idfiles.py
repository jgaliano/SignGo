# Generated by Django 5.0.6 on 2024-10-04 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eSignAnyWhere', '0006_firmante_envelope'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='estatus',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='firmante',
            name='idFiles',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
