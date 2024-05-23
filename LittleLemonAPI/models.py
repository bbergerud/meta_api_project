from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


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
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("title", "category")


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("menuitem", "user")

    def get_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_price()
        super().save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
    )
    date = models.DateField(db_index=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
    )

    class Meta:
        unique_together = ("order", "menuitem")

    def get_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        self.price = self.get_price()
        super().save(*args, **kwargs)
