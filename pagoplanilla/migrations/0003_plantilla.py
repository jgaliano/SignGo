# Generated by Django 5.0.6 on 2024-10-17 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagoplanilla', '0002_listacontactos_delete_lista_contactos_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plantilla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=50)),
                ('Contenido', models.TextField()),
            ],
        ),
    ]
