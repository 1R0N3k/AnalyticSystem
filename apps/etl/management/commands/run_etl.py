import time
from contextlib import suppress

from catalog.models import Category, Product
from customers.models import Customer
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from orders.models import Order, OrderItem

from etl.generators import generate_mock_orders
from etl.loader import load_orders


class Command(BaseCommand):
    help = 'Генерирует и загружает тестовые заказы в базу данных'

    def add_arguments(self, parser):
        """Определяем аргументы команды."""
        parser.add_argument(
            '--rows',
            type=int,
            default=1000,
            help='Количество заказов для генерации (по умолчанию: 1000)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить таблицы перед загрузкой',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Размер батча для генерации (по умолчанию: 500)',
        )

    def handle(self, *args, **options):
        rows = options['rows']
        clear = options['clear']
        batch_size = options['batch_size']

        if rows <= 0:
            raise CommandError('Количество заказов должно быть больше 0')
        if batch_size <= 0:
            raise CommandError('Размер батча должен быть больше 0')

        self.stdout.write(self.style.SUCCESS('\nЗапуск ETL-конвейера'))
        self.stdout.write(f'План: {rows} заказов')
        self.stdout.write(f'Размер батча: {batch_size}\n')

        if clear:
            self._clear_database()

        stats_before = self._get_stats()
        start_time = time.time()

        loaded_total = 0
        batches_count = (rows + batch_size - 1) // batch_size

        try:
            for batch_num in range(1, batches_count + 1):
                current_batch_size = min(batch_size, rows - loaded_total)

                self.stdout.write(
                    f'Батч {batch_num}/{batches_count} '
                    f'({current_batch_size} заказов)...',
                    ending=''
                )

                batch_start = time.time()

                orders = generate_mock_orders(current_batch_size)

                loaded = load_orders(orders)
                loaded_total += loaded

                batch_time = time.time() - batch_start
                self.stdout.write(
                    self.style.SUCCESS(f'({batch_time:.2f}с)')
                )

        except Exception as e:
            raise CommandError(f'Ошибка при загрузке данных: {e}') from e

        total_time = time.time() - start_time
        stats_after = self._get_stats()

        self.stdout.write(self.style.SUCCESS('\nETL-конвейер завершён!'))
        self._print_statistics(stats_before, stats_after, total_time, loaded_total)

    def _clear_database(self):
        """Очищает все таблицы, связанные с заказами."""
        self.stdout.write(self.style.WARNING('Очистка базы данных...'))

        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()

        with connection.cursor() as cursor:
            for table in [
                'orders_orderitem', 'orders_order', 'catalog_product',
                'catalog_category', 'customers_customer'
            ]:
                with suppress(Exception):
                    cursor.execute(
                        f'ALTER SEQUENCE {table}_id_seq RESTART WITH 1'
                    )

        self.stdout.write(self.style.SUCCESS('База очищена\n'))

    def _get_stats(self) -> dict:
        """Возвращает текущее количество записей в каждой таблице."""
        return {
            'customers': Customer.objects.count(),
            'categories': Category.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
        }

    def _print_statistics(
        self,
        stats_before: dict,
        stats_after: dict,
        total_time: float,
        loaded_total: int
    ):
        """Выводит красивую итоговую статистику."""
        self.stdout.write('\nСтатистика:')
        self.stdout.write(f'Клиентов в БД:     {stats_after["customers"]}')
        self.stdout.write(f'Категорий в БД:    {stats_after["categories"]}')
        self.stdout.write(f'Товаров в БД:      {stats_after["products"]}')
        self.stdout.write(f'Заказов в БД:      {stats_after["orders"]}')
        self.stdout.write(f'Позиций заказов:   {stats_after["order_items"]}')

        self.stdout.write(f'\nВремя выполнения: {total_time:.2f}с')
        self.stdout.write(
            f'Скорость: {loaded_total / total_time:.1f} заказов/сек'
            if total_time > 0 else ''
        )
        self.stdout.write('')
