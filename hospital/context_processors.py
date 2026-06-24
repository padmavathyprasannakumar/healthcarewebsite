from .models import SiteSetting


def site_info(request):
    try:
        setting = SiteSetting.objects.order_by('-created_at').first()
    except Exception:
        setting = None
    return {'site_setting': setting}
