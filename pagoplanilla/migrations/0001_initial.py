# Generated by Django 5.0.6 on 2024-10-16 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='contacto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombres', models.CharField(max_length=50)),
                ('Apellidos', models.CharField(max_length=50)),
                ('Email', models.CharField(max_length=50)),
                ('Celular', models.CharField(max_length=50)),
                ('Salario', models.CharField(max_length=50)),
                ('Departamento', models.CharField(max_length=50)),
                ('Puesto', models.CharField(max_length=50)),
                ('Periodo', models.CharField(max_length=50)),
                ('tokenAuth', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='lista_contactos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('tokenAuth', models.CharField(max_length=50)),
            ],
        ),
    ]
