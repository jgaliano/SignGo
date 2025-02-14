from django.db import migrations

def crearAuthPlanilla(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    group_names = ['planillaAuth']
    
    for group_name in group_names:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
            
class Migration(migrations.Migration):
    dependencies = [
        ('app', '0003_create_groups_permissions'), 
    ]

    operations = [
        migrations.RunPython(crearAuthPlanilla)
    ]