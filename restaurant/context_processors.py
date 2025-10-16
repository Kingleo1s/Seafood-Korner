from .models import CartItem, Cart

def cart_count(request):
    """Adds cart item count to all templates."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = CartItem.objects.filter(cart=cart).count()
    else:
        count = 0
    return {"cart_count": count}
