# Little Lemon APIs

This repository represents the final project as part of the [API](https://www.coursera.org/learn/apis) course in [Meta's Back-End Developer Professional Certificate](https://www.coursera.org/professional-certificates/meta-back-end-developer). It uses Django to interact with a sqlite database.


## Populating database
In the app LittleLemonAPI there is a fixtures directory that contains data for pre-populating the database tables. These data can be added to the database by running commands like the following:

```
>>> python manage.py loaddata groups.json
```

There is a [users.json](./LittleLemonAPI/fixtures/users.json) file, but the passwords are not correctly saved when running the loaddata command as they are not hashed when inserting.

The following files can be used to fill in the relevant data
- [category.json](./LittleLemonAPI/fixtures/category.json)
- [menuitem.json](./LittleLemonAPI/fixtures/menuitem.json)
- [order.json](./LittleLemonAPI/fixtures/order.json)
- [orderitem.json](./LittleLemonAPI/fixtures/orderitem.json)
- [cart.json](./LittleLemonAPI/fixtures/cart.json)

So to load them run the following in a terminal

```
python manage.py loaddata category.json menuitem.json order.json orderitem.json cart.json
```

## Testing
Tests are implemented to check that the code fullfills the grading rubric. These tests can be executed by running
```
>>> python manage.py test
```

and for testing a specific case (e.g., test_10) one can do

```
>>> python manage.py test LittleLemonAPI.tests.RubricTest.test_10
```

Here's a good [resource](https://b0uh.github.io/djangodrf-how-to-authenticate-a-user-in-tests.html) for authenticating users when testing.

<strong>NOTE</strong>: There is an issue with test #5 in regards to logging in which requires further debugging.

## Notes

Adding trailing slashes were removed in the [urls.py](./LittleLemon/urls.py) file, but the djoser paths still end with them so there are some API inconsistencies.
