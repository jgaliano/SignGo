# Generated by Django 5.0.6 on 2025-01-06 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_alter_licenciassistema_consumo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='renovacionlicencia',
            old_name='costo_renovacion_creditos',
            new_name='costo_creditos',
        ),
        migrations.RenameField(
            model_name='renovacionlicencia',
            old_name='costo_renovacion_licencia',
            new_name='costo_tipo',
        ),
        migrations.RenameField(
            model_name='renovacionlicencia',
            old_name='nueva_fecha_fin',
            new_name='fecha_fin',
        ),
        migrations.RenameField(
            model_name='renovacionlicencia',
            old_name='nueva_fecha_emisión',
            new_name='fecha_inicio',
        ),
    ]
