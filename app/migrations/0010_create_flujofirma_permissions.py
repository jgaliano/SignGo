from django.db import migrations

def crearAuthPlanilla(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    group_names = ['FlujoFirmaNormalAuth', 'FlujoFirmaAdminAuth']
    
    for group_name in group_names:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
            
class Migration(migrations.Migration):
    dependencies = [
        ('app', '0009_perfilsistema_token'), 
    ]

    operations = [
        migrations.RunPython(crearAuthPlanilla)
    ]