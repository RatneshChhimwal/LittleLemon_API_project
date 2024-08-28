from django.db import models
from django.contrib.auth.models import User
from django.db import models, transaction

class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.title

class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')

    def __str__(self):
        return f"{self.title} (${self.price:.2f})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2, editable=False)

    class Meta:
        unique_together = ('menuitem', 'user')

    def save(self, *args, **kwargs):
        self.price = self.menuitem.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart: {self.user.username} - {self.menuitem.title} x {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    status = models.BooleanField(default=False, db_index=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, editable=False, default=0)
    date = models.DateField(db_index=True)

    def save(self, *args, **kwargs):
        # Check if the order is being created for the first time
        if self.pk is None:  # This means it's a new order
            super().save(*args, **kwargs)  # Save the order first to get the ID
            cart_items = Cart.objects.filter(user=self.user)
            for item in cart_items:
                OrderItem.objects.create(
                    order=self,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    price=item.price
                )
            self.total = self.calculate_total()
            super().save(*args, **kwargs)  # Save again to update the total
        else:
            # For updates, just calculate and update the total
            self.total = self.calculate_total()
            super().save(*args, **kwargs)

    def calculate_total(self):
        return sum(item.price for item in self.order_items.all())

    def __str__(self):
        return f"Order by {self.user.username} on {self.date}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

    def __str__(self):
        return f"{self.order.user.username} - {self.menuitem.title} x {self.quantity}"
