# Generated by Django 5.0.6 on 2024-12-25 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flujofirma', '0015_log_oneshot_detail_log_oneshot_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmante',
            name='is_enviado',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
