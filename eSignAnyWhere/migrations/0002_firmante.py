# Generated by Django 5.0.6 on 2024-10-03 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eSignAnyWhere', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='firmante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombres', models.CharField(max_length=100)),
                ('apellidos', models.CharField(max_length=100)),
                ('correo', models.CharField(max_length=100)),
            ],
        ),
    ]
