from django.http import HttpResponse


def index(request):
    return HttpResponse('Hello from mysite.views')


# Optional simple error handlers (Django will use default handlers if these
# are not present). Defining them prevents attribute lookup errors if
# code expects them on the URLConf module.
def handler404(request, exception=None):
    return HttpResponse('Page not found', status=404)


def handler500(request):
    return HttpResponse('Server error', status=500)
