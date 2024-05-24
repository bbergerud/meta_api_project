import datetime as dt

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from . import models

# These aren't being used
MANAGER = dict(username="Woody", password="tomhanks")
CUSTOMER = dict(username="Buzz", password="timallen")


# Create your tests here.
class RubricTest(APITestCase):
    def setUp(self):

        # Make manager staff
        group_manager = Group.objects.create(name="Manager")
        group_crew = Group.objects.create(name="Delivery Crew")

        woody = User.objects.create(**MANAGER, is_staff=True)
        slinky = User.objects.create(username="Slinky", password="jimvarney")
        rex = User.objects.create(username="Rex", password="wallaceshawn")
        buzz = User.objects.create(**CUSTOMER)
        bo_peep = User.objects.create(username="Bo_Peep", password="anniepotts")

        for manager in [woody]:
            manager.groups.add(group_manager)

        for crew in [slinky, rex]:
            crew.groups.add(group_crew)

        cat_main = models.Category.objects.create(title="Main", slug="main")
        cat_app = models.Category.objects.create(title="Appetizer", slug="appetizer")
        cat_drink = models.Category.objects.create(title="Drink", slug="drink")

        menu = []
        for data in [
            dict(title="Beef Pasta", price=6.00, featured=False, category=cat_main),
            dict(title="Cheese Sticks", price=5.00, featured=False, category=cat_app),
            dict(title="Negroni", price=5.00, featured=False, category=cat_drink),
            dict(title="Bruschetta", price=10.00, featured=False, category=cat_main),
            dict(title="Greek Salad", price=7.50, featured=False, category=cat_app),
            dict(title="Bellini", price=5.00, featured=False, category=cat_drink),
        ]:
            menu.append(models.MenuItem.objects.create(**data))

        order = []
        for x in [
            dict(
                user=buzz,
                total=32,
                date=dt.date.today() - dt.timedelta(days=1),
                delivery_crew=slinky,
            ),
            dict(
                user=bo_peep,
                total=35,
                date=dt.date.today(),
                delivery_crew=rex,
            ),
        ]:
            order.append(models.Order.objects.create(**x))

        order_items = []
        for x in [
            dict(order=order[0], menuitem=menu[0], quantity=2),
            dict(order=order[0], menuitem=menu[1], quantity=2),
            dict(order=order[0], menuitem=menu[2], quantity=2),
            dict(order=order[1], menuitem=menu[3], quantity=2),
            dict(order=order[1], menuitem=menu[4], quantity=2),
            dict(order=order[1], menuitem=menu[5], quantity=2),
        ]:
            order_items.append(
                models.OrderItem.objects.create(
                    **x,
                    unit_price=x["menuitem"].price,
                    price=x["quantity"] * x["menuitem"].price,
                )
            )

        cart_items = []
        for x in [
            dict(user=buzz, menuitem=menu[0], quantity=2),
            dict(user=buzz, menuitem=menu[1], quantity=2),
        ]:
            cart_items.append(
                models.Cart.objects.create(
                    **x,
                    unit_price=x["menuitem"].price,
                    price=x["quantity"] * x["menuitem"].price,
                )
            )

        Token.objects.create(user=buzz)
        Token.objects.create(user=slinky)
        Token.objects.create(user=rex)
        Token.objects.create(user=woody)
        Token.objects.create(user=bo_peep)

    def test_01(self):
        """The admin can assign users to the manager group"""
        url = "/api/groups/manager/users"

        candidate = User.objects.filter(groups__name="Delivery Crew").first()
        data = {"username": candidate.username}

        manager = User.objects.filter(username=MANAGER["username"]).first()
        token = Token.objects.get(user=manager)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response)
        self.assertTrue(User.objects.filter(groups__name="Manager", **data).exists())

    def test_02(self):
        """You can access the manager group with a manager token"""
        url = "/api/groups/manager/users"

        user = User.objects.filter(username=MANAGER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_03(self):
        """The manager can add menu items"""
        url = "/api/menu-items"

        data = {
            "title": "Test",
            "price": 10.00,
            "category_id": 1,
        }

        user = User.objects.filter(username=MANAGER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.MenuItem.objects.filter(title="Test").exists())

    def test_04(self):
        """The manager can add categories"""
        url = "/api/categories"

        data = {
            "title": "Test",
            "slug": "test",
        }

        user = User.objects.filter(username=MANAGER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Category.objects.filter(title="Test").exists())

    def test_05(self):
        """Managers can login"""
        user = User.objects.filter(groups__name="Manager").first()
        token = Token.objects.get(user=user)

        # self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        # self.client.force_login(user)
        self.assertTrue(
            self.client.login(user=user),
            {
                "username": user.username,
                "password": user.password,
                "is_staff": user.is_staff,
            },
        )

    def test_06(self):
        """Managers can update the item of the day"""
        url = "/api/menu-items/featured/1"

        user = User.objects.filter(username=MANAGER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_07(self):
        """Managers can assign users to the delivery crew"""
        url = "/api/groups/delivery-crew/users"
        manager = User.objects.filter(groups__name="Manager").first()
        token = Token.objects.get(user=manager)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url, {"username": CUSTOMER["username"]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            User.objects.filter(
                username=CUSTOMER["username"],
                groups__name="Delivery Crew",
            ).exists()
        )

    def test_08(self):
        """Managers can assign orders to the delivery crew"""
        url = "/api/orders/1"

        crew = User.objects.filter(groups__name="Delivery Crew").last()
        manager = User.objects.filter(groups__name="Manager").first()
        token = Token.objects.get(user=manager)

        # Update delivery crew
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.put(url, {"delivery_crew_id": crew.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make sure delivery crew is correct
        order = models.Order.objects.filter(id=1).first()
        self.assertEqual(order.delivery_crew, crew)

    def test_09(self):
        """The delivery crew can access orders assigned to them"""
        url = "/api/orders"

        crew = User.objects.filter(groups__name="Delivery Crew").first()
        token = Token.objects.get(user=crew)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        for data in response.data["results"]:
            self.assertEqual(data["delivery_crew"]["username"], crew.username)

    def test_10(self):
        """The delivery crew can update an order as delivered"""
        url = "/api/orders/1"
        order = models.Order.objects.first()
        token = Token.objects.get(user=order.delivery_crew)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.patch(url, {"status": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make sure status is updated
        order = models.Order.objects.first()
        self.assertTrue(order.status)

    def test_11(self):
        # 11 - create user
        url = "/api/users/"
        data = dict(username="guest", password="123ABCxyz!")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="guest").exists())

    def test_12(self):
        """generate token using username and password"""

        # TODO: Figure out why this is needed for the second half to work
        url = "/api/users/"
        credentials = dict(username="guest", password="123ABCxyz!")
        response = self.client.post(url, credentials)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/token/login"
        response = self.client.post(url, credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_13(self):
        """browse categories"""
        url = reverse("categories")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="Test 13")

    def test_14(self):
        """browse menu items"""
        url = "/api/menu-items"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="Test 14")

    def test_15(self):
        """filter menu items by category"""
        url = "/api/menu-items?category=main"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="Test 15: SC")
        for data in response.data["results"]:
            self.assertEqual(
                data["category"]["title"].lower(), "main", msg="Test 15: category"
            )

    def test_16(self):
        """paginate (assuming page size = 4)"""
        url = "/api/menu-items?page=2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="Test 16: SC")
        self.assertEqual(response.data["results"][0]["id"], 5, msg="Test 16: page")

    def test_17(self):
        """sort menu items by price"""
        url = "/api/menu-items?ordering=price"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="Test 17: SC")

        data = response.data["results"]
        for i, j in zip(data[:-1], data[1:]):
            self.assertLessEqual(i["price"], j["price"], msg="Test 17: sorted price")

    def test_18(self):
        """add menu items to cart"""
        url = "/api/cart/menu-items"

        user = User.objects.filter(username=CUSTOMER["username"]).first()
        token = Token.objects.get(user=user)

        menuitem = models.MenuItem.objects.filter(id=4).first()
        data = dict(
            menuitem_id=menuitem.id,
            quantity=2,
            unit_price=menuitem.price,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_19(self):
        """access cart items"""
        url = "/api/cart/menu-items"

        user = User.objects.filter(username=CUSTOMER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        for data in response.data["results"]:
            self.assertEqual(data["user"]["username"], user.username, response.data)

    def test_20(self):
        """Customers can place orders"""
        url = "/api/orders"

        user = User.objects.filter(username=CUSTOMER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_21(self):
        """Customers can browse their own orders"""
        url = "/api/orders"

        user = User.objects.filter(username=CUSTOMER["username"]).first()
        token = Token.objects.get(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

        for data in response.data["results"]:
            self.assertEqual(data["user"]["username"], user.username, response.data)
