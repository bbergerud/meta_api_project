import decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now


# NOTE: Use to join fixtures by title rather than pk
class CategoryManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True, unique=True)
    objects = CategoryManager()

    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_index=True,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("title", "category")

    def __str__(self) -> str:
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )

    class Meta:
        unique_together = ("menuitem", "user")

    def get_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
        default=None,
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )
    date = models.DateField(db_index=True, default=now)

    def __str__(self) -> str:
        return f"{self.user} | {self.date} | {self.total}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal("0.00"))],
    )

    class Meta:
        unique_together = ("order", "menuitem")

    def get_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_price()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Order {self.order.id} | {self.menuitem.title}"
