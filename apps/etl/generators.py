import random
from datetime import datetime, timezone
from decimal import Decimal

from faker import Faker

from .schemas import RawOrder, RawOrderItem

fake = Faker('ru_RU')

PRODUCT_CATALOG = {
    'Электроника': [
        ('Смартфон', Decimal('15000'), Decimal('50000')),
        ('Ноутбук', Decimal('40000'), Decimal('120000')),
        ('Планшет', Decimal('20000'), Decimal('60000')),
        ('Наушники', Decimal('2000'), Decimal('15000')),
        ('Умные часы', Decimal('5000'), Decimal('25000')),
    ],
    'Одежда': [
        ('Футболка', Decimal('800'), Decimal('3000')),
        ('Джинсы', Decimal('2000'), Decimal('7000')),
        ('Куртка', Decimal('5000'), Decimal('15000')),
        ('Кроссовки', Decimal('3000'), Decimal('12000')),
        ('Свитер', Decimal('2500'), Decimal('8000')),
    ],
    'Книги': [
        ('Роман', Decimal('400'), Decimal('1200')),
        ('Учебник', Decimal('600'), Decimal('2000')),
        ('Комикс', Decimal('500'), Decimal('1500')),
        ('Энциклопедия', Decimal('1500'), Decimal('4000')),
        ('Бизнес-литература', Decimal('500'), Decimal('1800')),
    ],
    'Дом и сад': [
        ('Настольная лампа', Decimal('1500'), Decimal('5000')),
        ('Ваза', Decimal('800'), Decimal('3000')),
        ('Набор инструментов', Decimal('2000'), Decimal('8000')),
        ('Кресло', Decimal('8000'), Decimal('25000')),
        ('Кашпо', Decimal('500'), Decimal('2000')),
    ],
    'Спорт': [
        ('Мяч футбольный', Decimal('1000'), Decimal('4000')),
        ('Гантели', Decimal('2000'), Decimal('8000')),
        ('Коврик для йоги', Decimal('800'), Decimal('3000')),
        ('Велосипед', Decimal('15000'), Decimal('50000')),
        ('Скакалка', Decimal('300'), Decimal('1500')),
    ],
}

STATUS_WEIGHTS = {
    'new': 0.10,        
    'paid': 0.45,       
    'delivered': 0.35,  
    'cancelled': 0.10,  
}

CITIES = [
    'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
    'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону',
    'Уфа', 'Красноярск', 'Воронеж', 'Пермь', 'Волгоград',
]


def _generate_random_price(min_price: Decimal, max_price: Decimal) -> Decimal:
    price = random.uniform(float(min_price), float(max_price))
    return Decimal(str(round(price, 2)))


def _generate_order_items(count: int) -> list[RawOrderItem]:
    items = []
    for _ in range(count):
        category_name = random.choice(list(PRODUCT_CATALOG.keys()))
        
        product_name, min_price, max_price = random.choice(PRODUCT_CATALOG[category_name])

        price = _generate_random_price(min_price, max_price)
        margin_percent = random.uniform(0.4, 0.7)
        cost = Decimal(str(round(float(price) * margin_percent, 2)))
        
        items.append(RawOrderItem(
            name=product_name,
            category=category_name,
            quantity=random.randint(1, 5),
            price=price,
            cost=cost,
        ))
    
    return items


def generate_mock_orders(count: int = 1000) -> list[RawOrder]:
    orders = []
    
    statuses = list(STATUS_WEIGHTS.keys())
    weights = list(STATUS_WEIGHTS.values())
    
    for _ in range(count):
        created_at = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)

        items_count = random.randint(1, 5)
        items_list = _generate_order_items(items_count)
        
        city = random.choice(CITIES)
        
        status = random.choices(statuses, weights=weights, k=1)[0]
        
        order = RawOrder(
            client_name=fake.first_name(),
            client_surname=fake.last_name(),
            client_email=fake.email(),
            city=city,
            items_list=items_list,
            created_at=created_at,
            status=status,
        )
        orders.append(order)
    
    return orders