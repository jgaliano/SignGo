# Generated by Django 5.0.6 on 2024-12-21 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujofirma', '0005_datosfirmante_firmante_imagen_imagen'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagen',
            old_name='UsuarioSistema',
            new_name='UsuarioFirmante',
        ),
    ]
