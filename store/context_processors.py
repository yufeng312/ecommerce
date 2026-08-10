from .models import Category


def categories(request):
    return {"categories": Category.objects.filter(parent=None).prefetch_related("children").all()}
