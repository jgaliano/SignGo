from django.db import migrations

def crearGrupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    group_names = ['SignboxAuth', 'OneshotAuth', 'VolAuth', '4identityAuth', 'eSignAuth']
    
    for group_name in group_names:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
            
class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_delete_billingsignbox'), 
    ]

    operations = [
        migrations.RunPython(crearGrupos)
    ]