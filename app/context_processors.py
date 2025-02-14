from django.contrib.auth.models import Group

def user_context_processor(request):
    return {
        'user': request.user
    }
    
def verificar_grupo(request):
    if request.user.is_authenticated:
        usuario_in_signbox = request.user.groups.filter(name='SignboxAuth').exists()
        usuario_in_oneshot = request.user.groups.filter(name='OneshotAuth').exists()
        usuario_in_vol = request.user.groups.filter(name='VolAuth').exists()
        usuario_in_4identity = request.user.groups.filter(name='4identityAuth').exists()
        usuario_in_esign = request.user.groups.filter(name='eSignAuth').exists()
        usuario_in_plantilla = request.user.groups.filter(name='planillaAuth').exists()
        usuario_in_signbol = request.user.groups.filter(name='SignbolAuth').exists()
        usuario_in_signbolContactos = request.user.groups.filter(name='SignbolContactosAuth').exists()
        usuario_in_signbolEnvios = request.user.groups.filter(name='SignbolEnviosAuth').exists()
        usuario_in_signbolReportes = request.user.groups.filter(name='SignbolReportesAuth').exists()
        usuario_in_signbolAdmin = request.user.groups.filter(name='SignbolAdminAuth').exists()
        usuario_normal_in_flujofirma = request.user.groups.filter(name='FlujoFirmaNormalAuth').exists()
        usuario_admin_in_flujofirma = request.user.groups.filter(name='FlujoFirmaAdminAuth').exists()
    else:
        usuario_in_signbox = False
        usuario_in_oneshot = False
        usuario_in_vol = False
        usuario_in_4identity = False
        usuario_in_esign = False
        usuario_in_plantilla = False
        usuario_in_signbol = False
        usuario_in_signbolContactos = False
        usuario_in_signbolEnvios = False
        usuario_in_signbolReportes = False
        usuario_in_signbolAdmin = False
        usuario_normal_in_flujofirma = False
        usuario_admin_in_flujofirma = False
        
    contexto = {
        'usuario_in_signbox': usuario_in_signbox,
        'usuario_in_oneshot': usuario_in_oneshot,
        'usuario_in_vol': usuario_in_vol,
        'usuario_in_4identity': usuario_in_4identity,
        'usuario_in_esign': usuario_in_esign,
        'usuario_in_plantilla': usuario_in_plantilla,
        'usuario_in_signbol': usuario_in_signbol,
        'usuario_in_signbolContactos': usuario_in_signbolContactos,
        'usuario_in_signbolEnvios': usuario_in_signbolEnvios,
        'usuario_in_signbolReportes': usuario_in_signbolReportes,
        'usuario_in_signbolAdmin': usuario_in_signbolAdmin,
        'usuario_normal_in_flujofirma': usuario_normal_in_flujofirma,
        'usuario_admin_in_flujofirma': usuario_admin_in_flujofirma
    }
    return contexto