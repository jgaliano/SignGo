# Generated by Django 5.0.6 on 2024-10-03 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eSignAnyWhere', '0004_firmante_sobre_firmante_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmante',
            name='request',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
