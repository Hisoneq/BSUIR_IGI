from django.core.validators import MinValueValidator
from django.test import TestCase
from decimal import Decimal
from datetime import date
from users.models import User, Employee, Client
from ..models import (
    Property,
    ServiceType,
    PropertyService,
    Transaction,
    PropertyInquiry,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def create_user_with_role(username, role):
    return User.objects.create(
        username=username,
        role=role,
        phone_number='+375(29)000-00-00',
        birth_date=date(1990, 1, 1),
        first_name=username.capitalize(),
        last_name='Test',
    )


class ServiceTypeTests(TestCase):
    def setUp(self):
        self.stype = ServiceType.objects.create(title="Тип услуги")

    def test_title_field(self):
        self.assertEqual(self.stype._meta.get_field("title").max_length, 200)
        self.assertEqual(str(self.stype), self.stype.title)


class PropertyServiceTests(TestCase):
    def setUp(self):
        self.stype = ServiceType.objects.create(title="Категория")
        self.service = PropertyService.objects.create(
            title="Сервис 1", service_type=self.stype, price=Decimal("123.45")
        )

    def test_service_fields(self):
        self.assertEqual(self.service.title, "Сервис 1")
        self.assertEqual(self.service.service_type, self.stype)
        self.assertEqual(self.service.price, Decimal("123.45"))
        self.assertIn("title", [f.name for f in self.service._meta.fields])
        self.assertTrue(str(self.service).startswith("(") or str(self.service).endswith(self.service.title))


class PropertyTests(TestCase):
    def setUp(self):
        self.stype = ServiceType.objects.create(title="Жильё")
        self.service = PropertyService.objects.create(title="Сервис", service_type=self.stype, price=Decimal("100.00"))
        self.prop = Property.objects.create(
            price=Decimal("100000.00"),
            square_meters=Decimal("50.00"),
            category=self.service,
            description="Описание недвижимости",
            address="Test Address 123",
        )

    def test_property_fields(self):
        self.assertEqual(self.prop.price, Decimal("100000.00"))
        self.assertEqual(self.prop.square_meters, Decimal("50.00"))
        self.assertEqual(self.prop.category, self.service)
        self.assertEqual(self.prop.address, "Test Address 123")
        self.assertTrue("description" in [f.name for f in self.prop._meta.fields])
        self.assertTrue(str(self.prop).startswith(self.prop.address))


class TransactionTests(TestCase):
    def setUp(self):
        self.client_user = create_user_with_role("client_user", "client")
        self.employee_user = create_user_with_role("employee_user", "employee")
        self.client = Client.objects.create(user=self.client_user)
        self.employee = Employee.objects.create(user=self.employee_user, hire_date=date(2010, 1, 1))
        self.stype = ServiceType.objects.create(title="Транзакция")
        self.service = PropertyService.objects.create(title="Сервис", service_type=self.stype, price=Decimal("100.00"))
        self.prop = Property.objects.create(
            price=Decimal("100000.00"),
            square_meters=Decimal("50.00"),
            category=self.service,
            description="desc",
            address="Somewhere",
        )
        self.trans = Transaction.objects.create(
            client=self.client,
            agent=self.employee,
            property=self.prop,
        )

    def test_transaction_relations(self):
        self.assertEqual(self.trans.client, self.client)
        self.assertEqual(self.trans.agent, self.employee)
        self.assertEqual(self.trans.property, self.prop)
        self.assertTrue(hasattr(self.trans, 'transaction_date'))
        self.assertTrue(str(self.trans).count('-') > 0)


class PropertyInquiryTests(TestCase):
    def setUp(self):
        self.client_user = create_user_with_role("client_user", "client")
        self.employee_user = create_user_with_role("employee_user", "employee")
        self.client = Client.objects.create(user=self.client_user)
        self.employee = Employee.objects.create(user=self.employee_user, hire_date=date(2010, 1, 1))
        self.stype = ServiceType.objects.create(title="Запрос")
        self.service = PropertyService.objects.create(title="Сервис", service_type=self.stype, price=Decimal("100.00"))
        self.prop = Property.objects.create(
            price=Decimal("100000.00"),
            square_meters=Decimal("50.00"),
            category=self.service,
            description="desc",
            address="Somewhere",
        )
        self.inquiry = PropertyInquiry.objects.create(
            property=self.prop,
            client=self.client,
            employee=self.employee,
            inquiry_text="Вопрос по объекту",
        )

    def test_inquiry_fields(self):
        self.assertEqual(self.inquiry.property, self.prop)
        self.assertEqual(self.inquiry.client, self.client)
        self.assertEqual(self.inquiry.employee, self.employee)
        self.assertTrue(hasattr(self.inquiry, 'created_at'))
        self.assertTrue(hasattr(self.inquiry, 'state') or hasattr(self.inquiry, 'status'))
        self.assertTrue(str(self.inquiry).find(self.client_user.username) > -1)


class PropertyModelTest(TestCase):
    """Test suite for Property model"""
    
    def setUp(self):
        self.service_type = PropertyService.objects.create(
            title="Test Service",
            service_fee=Decimal('100.00')
        )
        self.property = Property.objects.create(
            price=Decimal('100000.00'),
            square_meters=Decimal('100.00'),
            property_type=self.service_type,
            details="Test property",
            location="Test Location"
        )

    def test_property_creation(self):
        """Test property creation with valid data"""
        self.assertEqual(self.property.price, Decimal('100000.00'))
        self.assertEqual(self.property.square_meters, Decimal('100.00'))
        self.assertEqual(self.property.property_type, self.service_type)

    def test_property_validation(self):
        """Test property validation rules"""
        with self.assertRaises(ValidationError):
            Property.objects.create(
                price=Decimal('-100.00'),
                square_meters=Decimal('100.00'),
                property_type=self.service_type,
                details="Test property",
                location="Test Location"
            )

    def test_property_str_representation(self):
        """Test property string representation"""
        expected_str = f"{self.property.location}: {self.property.price}"
        self.assertEqual(str(self.property), expected_str)


class TransactionModelTest(TestCase):
    """Test suite for Transaction model"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.client = Client.objects.create(user=self.user)
        self.employee = Employee.objects.create(
            user=CustomUser.objects.create_user(
                username="testemployee",
                password="testpass"
            )
        )
        self.service_type = PropertyService.objects.create(
            title="Test Service",
            service_fee=Decimal('100.00')
        )
        self.property = Property.objects.create(
            price=Decimal('100000.00'),
            square_meters=Decimal('100.00'),
            property_type=self.service_type,
            details="Test property",
            location="Test Location"
        )

    def test_transaction_creation(self):
        """Test transaction creation with valid data"""
        transaction = Transaction.objects.create(
            buyer=self.client,
            agent=self.employee,
            property=self.property
        )
        self.assertEqual(transaction.total_amount, Decimal('100100.00'))

    def test_transaction_date_auto_set(self):
        """Test automatic date setting for transactions"""
        transaction = Transaction.objects.create(
            buyer=self.client,
            agent=self.employee,
            property=self.property
        )
        self.assertIsNotNone(transaction.contract_date)
        self.assertIsNotNone(transaction.transaction_date)


class PropertyInquiryModelTest(TestCase):
    """Test suite for PropertyInquiry model"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.client = Client.objects.create(user=self.user)
        self.employee = Employee.objects.create(
            user=CustomUser.objects.create_user(
                username="testemployee",
                password="testpass"
            )
        )
        self.service_type = PropertyService.objects.create(
            title="Test Service",
            service_fee=Decimal('100.00')
        )
        self.property = Property.objects.create(
            price=Decimal('100000.00'),
            square_meters=Decimal('100.00'),
            property_type=self.service_type,
            details="Test property",
            location="Test Location"
        )

    def test_inquiry_creation(self):
        """Test inquiry creation with valid data"""
        inquiry = PropertyInquiry.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee,
            inquiry_text="Test inquiry"
        )
        self.assertEqual(inquiry.state, "pending")
        self.assertIsNotNone(inquiry.created_at)

    def test_inquiry_state_transition(self):
        """Test inquiry state transitions"""
        inquiry = PropertyInquiry.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee,
            inquiry_text="Test inquiry"
        )
        inquiry.state = "processing"
        inquiry.save()
        self.assertEqual(inquiry.state, "processing")

    def test_inquiry_unique_constraint(self):
        """Test unique constraint on property and buyer"""
        PropertyInquiry.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee,
            inquiry_text="Test inquiry"
        )
        with self.assertRaises(ValidationError):
            PropertyInquiry.objects.create(
                property=self.property,
                buyer=self.client,
                agent=self.employee,
                inquiry_text="Another inquiry"
            )

