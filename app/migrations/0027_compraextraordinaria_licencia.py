# Generated by Django 5.0.6 on 2025-01-19 00:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_compraextraordinaria'),
    ]

    operations = [
        migrations.AddField(
            model_name='compraextraordinaria',
            name='licencia',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='compra_extra', to='app.licenciassistema'),
        ),
    ]
