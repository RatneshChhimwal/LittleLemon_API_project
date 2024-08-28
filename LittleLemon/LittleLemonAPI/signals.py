from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Cart, OrderItem
import logging

@receiver(post_save, sender=Order)
def create_order_items(sender, instance, created, **kwargs):
    if created:
        logging.info(f"Order created: {instance}")
        # Create OrderItem instances for each item in the user's cart
        cart_items = Cart.objects.filter(user=instance.user)
        for item in cart_items:
            logging.info(f"Adding {item.menuitem.title} to order {instance.id}")
            OrderItem.objects.create(
                order=instance,
                menuitem=item.menuitem,
                quantity=item.quantity,
                price=item.price
            )
        # Update the order total
        instance.total = instance.calculate_total()
        instance.save()

