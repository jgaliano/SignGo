# Generated by Django 5.0.6 on 2025-01-19 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_licenciassistema_env'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompraExtraordinaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_creditos', models.IntegerField()),
                ('precio_creditos', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fecha_compra', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
