# Generated by Django 5.0.6 on 2024-12-30 18:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flujofirma', '0020_vitacorafirmado'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoIdentificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.TextField()),
                ('date', models.DateTimeField()),
                ('previous_status', models.TextField()),
                ('request', models.CharField(max_length=15)),
                ('registration_authority', models.CharField(max_length=10)),
                ('firmante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='firmante_video', to='flujofirma.firmante')),
            ],
        ),
    ]
