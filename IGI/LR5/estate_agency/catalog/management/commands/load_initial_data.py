from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date
from catalog.models import ServiceCategory, Service, Estate
from home.models import (
    AboutCompany, News, FAQ, Contact, 
    Vacancy, Review, PromoCode, Policy
)
from users.models import User, Client, Employee

class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **kwargs):
        # Очищаем существующие данные
        User.objects.filter(username__in=['test', 'employee']).delete()
        
        # Создаем тестового пользователя для отзывов
        test_user = User.objects.create_user(
            username='test',
            password='123',
            first_name='test',
            last_name='test',
            role='client',
            phone_number='+375(29)123-45-67',
            birth_date='2001-10-10'
        )
        client = Client.objects.create(user=test_user)

        # Создаем сотрудника
        employee_user = User.objects.create_user(
            username='employee',
            password='empl123',
            first_name='123',
            last_name='123',
            role='employee',
            phone_number='+375(29)765-43-21',
            birth_date='2001-01-01'
        )
        employee = Employee.objects.create(
            user=employee_user,
            hire_date=date(2023, 1, 1)
        )

        # Создаем информацию о компании
        AboutCompany.objects.create(
            text="Мы - ведущее агентство недвижимости, работающее на рынке более 10 лет. "
                 "Наша миссия - помогать людям находить идеальное жилье и делать выгодные инвестиции в недвижимость."
        )

        # Создаем новости
        News.objects.create(
            title="Новые квартиры в центре города",
            summary="Мы рады представить новые апартаменты в самом сердце города. "
                   "Современный дизайн, удобное расположение и доступные цены."
        )
        News.objects.create(
            title="Скидки на услуги агентства",
            summary="В честь нашего 10-летнего юбилея мы предлагаем специальные скидки "
                   "на все услуги агентства до конца месяца."
        )

        # Создаем FAQ
        FAQ.objects.create(
            question="Как выбрать подходящую недвижимость?",
            answer="При выборе недвижимости важно учитывать множество факторов: "
                  "местоположение, бюджет, размер, инфраструктуру и т.д. "
                  "Наши специалисты помогут вам сделать правильный выбор."
        )
        FAQ.objects.create(
            question="Какие документы нужны для покупки недвижимости?",
            answer="Для покупки недвижимости вам понадобятся: паспорт, "
                  "справка о доходах, документы о праве собственности на продаваемый объект "
                  "и другие документы в зависимости от конкретной ситуации."
        )

        # Создаем контакты
        Contact.objects.create(
            name="Анна Петрова",
            position="Руководитель отдела продаж",
            description="Опытный специалист с 8-летним стажем работы в сфере недвижимости.",
            phone="+375(29)111-22-33",
            email="anna@example.com"
        )
        Contact.objects.create(
            name="Иван Иванов",
            position="Ведущий специалист",
            description="Эксперт по коммерческой недвижимости.",
            phone="+375(29)444-55-66",
            email="ivan@example.com"
        )

        # Создаем вакансии
        Vacancy.objects.create(
            position="Агент по недвижимости",
            salary=1000,
            description="Требуется опытный агент по недвижимости. "
                      "Опыт работы от 2 лет, знание рынка недвижимости."
        )
        Vacancy.objects.create(
            position="Юрист по недвижимости",
            salary=1500,
            description="Требуется юрист со знанием законодательства в сфере недвижимости. "
                      "Опыт работы от 3 лет."
        )

        # Создаем отзывы
        Review.objects.create(
            user=test_user,
            rating=5,
            text="Отличный сервис! Помогли найти идеальную квартиру в короткие сроки."
        )
        Review.objects.create(
            user=test_user,
            rating=4,
            text="Хорошая работа агентства. Единственное пожелание - больше вариантов в центре города."
        )

        # Создаем промокоды
        PromoCode.objects.create(
            code="WELCOME10",
            discount=10,
            description="Скидка 10% для новых клиентов",
            status=True
        )
        PromoCode.objects.create(
            code="SUMMER20",
            discount=20,
            description="Летняя скидка 20% на все услуги",
            status=True
        )

        # Создаем категории услуг
        categories = {
            'sale': ServiceCategory.objects.create(name='Продажа недвижимости'),
            'rent': ServiceCategory.objects.create(name='Аренда недвижимости'),
            'consult': ServiceCategory.objects.create(name='Консультации'),
            'evaluation': ServiceCategory.objects.create(name='Оценка недвижимости'),
        }

        # Создаем услуги
        services = {
            'sale_apartment': Service.objects.create(
                name='Продажа квартиры',
                category=categories['sale'],
                cost=Decimal('1000.00')
            ),
            'sale_house': Service.objects.create(
                name='Продажа дома',
                category=categories['sale'],
                cost=Decimal('1500.00')
            ),
            'rent_apartment': Service.objects.create(
                name='Аренда квартиры',
                category=categories['rent'],
                cost=Decimal('500.00')
            ),
            'rent_office': Service.objects.create(
                name='Аренда офиса',
                category=categories['rent'],
                cost=Decimal('800.00')
            ),
            'mortgage_consult': Service.objects.create(
                name='Консультация по ипотеке',
                category=categories['consult'],
                cost=Decimal('300.00')
            ),
            'investment_consult': Service.objects.create(
                name='Консультация по инвестициям',
                category=categories['consult'],
                cost=Decimal('400.00')
            ),
            'apartment_evaluation': Service.objects.create(
                name='Оценка квартиры',
                category=categories['evaluation'],
                cost=Decimal('200.00')
            ),
            'commercial_evaluation': Service.objects.create(
                name='Оценка коммерческой недвижимости',
                category=categories['evaluation'],
                cost=Decimal('300.00')
            ),
        }

        # Создаем объекты недвижимости
        Estate.objects.create(
            address='ул. Ленина, 10, кв. 5',
            cost=Decimal('150000.00'),
            area=Decimal('75.50'),
            category=services['sale_apartment'],
            description='Просторная трехкомнатная квартира в центре города'
        )

        Estate.objects.create(
            address='ул. Садовая, 25',
            cost=Decimal('350000.00'),
            area=Decimal('150.00'),
            category=services['sale_house'],
            description='Загородный дом с участком'
        )

        Estate.objects.create(
            address='пр. Мира, 15, офис 301',
            cost=Decimal('25000.00'),
            area=Decimal('100.00'),
            category=services['rent_office'],
            description='Офисное помещение в бизнес-центре'
        )

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена'))