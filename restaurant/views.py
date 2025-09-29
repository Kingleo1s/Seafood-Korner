from django.shortcuts import render
from .models import MenuItem

def menu(request):
    items = MenuItem.objects.all()
    return render(request, "restaurant/menu.html", {"menu_items": items})
