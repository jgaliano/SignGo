# Generated by Django 5.0.6 on 2024-10-01 17:10

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='documentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreArchivos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200, null=True), size=None)),
                ('nombreCarpeta', models.CharField(max_length=250)),
                ('request', models.CharField(max_length=10, null=True)),
            ],
        ),
    ]
