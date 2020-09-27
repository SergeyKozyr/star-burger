from django.db import models
from django.utils import timezone
from django.core.cache import cache
from utilities.utils import fetch_coordinates, get_distance
from operator import itemgetter


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def coordinates(self):
        lon, lat = fetch_coordinates(self.address)
        return lat, lon

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    ingridients = models.CharField('ингредиенты', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class Order(models.Model):
    firstname = models.CharField('Имя', max_length=15)
    lastname = models.CharField('Фамилия', max_length=30)
    phonenumber = models.CharField('Номер телефона', max_length=12)
    address = models.CharField('Адрес', max_length=100)

    STATUS_CHOICES = [
        ('processed', 'Обработанный'),
        ('unprocessed', 'Необработанный')
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличными'),
        ('online', 'Электронно')
    ]

    status = models.CharField('Статус', max_length=11, choices=STATUS_CHOICES, default='unprocessed')
    payment_method = models.CharField('Способ оплаты', max_length=6, choices=PAYMENT_CHOICES, default='online')
    comment = models.TextField('Комментарий', blank=True)
    registered_at = models.DateTimeField('Время создания заказа', default=timezone.now)
    called_at = models.DateTimeField('Время звонка', blank=True, null=True)
    delivered_at = models.DateTimeField('Время доставки', blank=True, null=True)

    def order_restaurants(self):
        order_items = self.items.all()
        restaurant_items = set()
        lon, lat = fetch_coordinates(self.address)
        for order_item in order_items:
            restaurant_items.update(order_item.product.menu_items.filter(availability=True))

        restaurants = {(order_item.restaurant, get_distance((lat, lon), order_item.restaurant.coordinates())) for order_item in restaurant_items}

        return sorted(restaurants, key=itemgetter(1))

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='товар', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField('Количество')
    price = models.PositiveSmallIntegerField('Стоимость')

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f'{self.product} {self.quantity} шт. - {self.order}'

    # @property
    # def total_price(self):
    #     return int(self.product.price * self.quantity)
