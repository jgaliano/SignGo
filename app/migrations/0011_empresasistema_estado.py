# Generated by Django 5.0.6 on 2024-12-15 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_create_flujofirma_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresasistema',
            name='Estado',
            field=models.BooleanField(default=True),
        ),
    ]
