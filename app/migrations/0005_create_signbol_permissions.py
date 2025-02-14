from django.db import migrations

def crearAuthPlanilla(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    group_names = ['SignbolAuth', 'SignbolContactosAuth', 'SignbolEnviosAuth', 'SignbolReportesAuth', 'SignbolAdminAuth']
    
    for group_name in group_names:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
            
class Migration(migrations.Migration):
    dependencies = [
        ('app', '0004_create_planilla_permissions'), 
    ]

    operations = [
        migrations.RunPython(crearAuthPlanilla)
    ]