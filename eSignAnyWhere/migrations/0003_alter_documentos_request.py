# Generated by Django 5.0.6 on 2024-10-03 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eSignAnyWhere', '0002_firmante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentos',
            name='request',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
