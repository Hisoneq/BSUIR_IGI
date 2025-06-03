from datetime import datetime
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..views import (
    PropertyServiceListView,
    AvailablePropertyListView,
    PropertyDetailView,
    ClientDashboardView,
    EmployeeDashboardView,
)
from ..models import PropertyService, ServiceType, Property, Transaction, PropertyInquiry
from users.models import Client as UserClient, Employee, User

def create_user(username, role, password='testpass'):
    return User.objects.create_user(
        first_name=username,
        last_name="Test",
        role=role,
        phone_number="+375(29)777-77-77",
        birth_date=datetime(2000, 1, 1),
        username=username,
        password=password,
    )

class ViewTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user("client", "client")
        cls.client_obj = UserClient.objects.create(user=cls.user)
        cls.employee_user = create_user("employee", "employee")
        cls.employee = Employee.objects.create(user=cls.employee_user, hire_date=datetime(2000, 1, 1))
        cls.stype = ServiceType.objects.create(title='Категория')
        cls.service = PropertyService.objects.create(title='Service1', price=100, service_type=cls.stype)
        cls.property = Property.objects.create(
            address='123 Test St',
            price=100000,
            square_meters=100,
            description='Test Property',
            category=cls.service
        )
        cls.factory = RequestFactory()

    def login(self, username='client', password='testpass'):
        self.client.login(username=username, password=password)

class PropertyServiceListViewTest(ViewTestBase):
    def test_queryset_and_context(self):
        request = self.factory.get(reverse('service_list'), {'min_price': 50, 'max_price': 150})
        view = PropertyServiceListView.as_view()
        response = view(request)
        self.assertIn(self.service, list(response.context_data['object_list']))
        self.assertIn('service_categories', response.context_data)
        self.assertIn(self.stype, list(response.context_data['service_categories']))

class AvailablePropertyListViewTest(ViewTestBase):
    def test_queryset_filters(self):
        self.login()
        request = self.factory.get(reverse('property_list'), {'search': 'Test St'})
        request.user = self.user
        view = AvailablePropertyListView.as_view()
        response = view(request)
        self.assertIn(self.property, list(response.context_data['object_list']))

    def test_context_data(self):
        self.login()
        request = self.factory.get(reverse('property_list'))
        request.user = self.user
        view = AvailablePropertyListView.as_view()
        response = view(request)
        self.assertIn('categories', response.context_data)
        self.assertIn('service_categories', response.context_data)

    def test_unauthenticated_redirect(self):
        response = self.client.get(reverse('property_list'))
        self.assertEqual(response.status_code, 302)

class PropertyDetailViewTest(ViewTestBase):
    def test_context_for_authenticated(self):
        self.login()
        PropertyInquiry.objects.create(client=self.client_obj, property=self.property, state='new')
        request = self.factory.get(reverse('property_detail', kwargs={'pk': self.property.id}))
        request.user = self.user
        view = PropertyDetailView.as_view()
        response = view(request, pk=self.property.id)
        self.assertTrue(response.context_data['request_exists'])

    def test_context_for_unauthenticated(self):
        response = self.client.get(reverse('property_detail', kwargs={'pk': self.property.id}))
        self.assertEqual(response.status_code, 302)

class ClientDashboardViewTest(ViewTestBase):
    def test_dashboard_context(self):
        self.login()
        PropertyInquiry.objects.create(client=self.client_obj, property=self.property, state='new')
        Transaction.objects.create(client=self.client_obj, property=self.property, agent=self.employee)
        request = self.factory.get(reverse('client_dashboard'))
        request.user = self.user
        view = ClientDashboardView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context_data['requests']), 1)
        self.assertGreaterEqual(len(response.context_data['sales']), 1)

    def test_post_buy(self):
        self.login()
        inquiry = PropertyInquiry.objects.create(client=self.client_obj, property=self.property, state='new', employee=self.employee)
        response = self.client.post(reverse('client_dashboard'), {'action': 'buy', 'request_id': inquiry.id})
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.state, 'completed')

    def test_post_cancel(self):
        self.login()
        inquiry = PropertyInquiry.objects.create(client=self.client_obj, property=self.property, state='new')
        response = self.client.post(reverse('client_dashboard'), {'action': 'cancel', 'request_id': inquiry.id})
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.state, 'completed')

    def test_post_invalid_id(self):
        self.login()
        response = self.client.post(reverse('client_dashboard'), {'action': 'buy', 'request_id': 999})
        self.assertEqual(response.status_code, 404)

class EmployeeDashboardViewTest(ViewTestBase):
    def test_employee_dashboard(self):
        self.client.login(username='employee', password='testpass')
        PropertyInquiry.objects.create(client=self.client_obj, property=self.property, employee=self.employee, state='new')
        Transaction.objects.create(client=self.client_obj, property=self.property, agent=self.employee)
        request = self.factory.get(reverse('employee_dashboard'))
        request.user = self.employee_user
        view = EmployeeDashboardView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context_data['clients']), 1)
        self.assertGreaterEqual(len(response.context_data['requests']), 1)
        self.assertGreaterEqual(len(response.context_data['sales']), 1)

    def test_no_employee(self):
        self.login()
        response = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('employee' in str(m) for m in messages))

class PropertyViewTest(TestCase):
    """Test suite for property-related views"""
    
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.client.login(username="testuser", password="testpass")
        
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

    def test_property_list_view(self):
        """Test property list view"""
        response = self.client.get(reverse('property_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'property_list.html')
        self.assertContains(response, self.property.location)

    def test_property_detail_view(self):
        """Test property detail view"""
        response = self.client.get(
            reverse('property_detail', kwargs={'pk': self.property.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'property_detail.html')
        self.assertContains(response, self.property.details)

    def test_property_search(self):
        """Test property search functionality"""
        response = self.client.get(
            reverse('property_list'),
            {'search': 'Test Location'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.location)

class TransactionViewTest(TestCase):
    """Test suite for transaction-related views"""
    
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.user_client = UserClient.objects.create(user=self.user)
        self.client.login(username="testuser", password="testpass")
        
        self.employee = Employee.objects.create(
            user=get_user_model().objects.create_user(
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
        """Test transaction creation view"""
        response = self.client.post(
            reverse('create_transaction'),
            {
                'property': self.property.pk,
                'buyer': self.user_client.pk,
                'agent': self.employee.pk
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Transaction.objects.filter(
                property=self.property,
                buyer=self.user_client
            ).exists()
        )

    def test_transaction_list_view(self):
        """Test transaction list view"""
        Transaction.objects.create(
            property=self.property,
            buyer=self.user_client,
            agent=self.employee
        )
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')

class PropertyInquiryViewTest(TestCase):
    """Test suite for property inquiry views"""
    
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.user_client = UserClient.objects.create(user=self.user)
        self.client.login(username="testuser", password="testpass")
        
        self.employee = Employee.objects.create(
            user=get_user_model().objects.create_user(
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
        """Test inquiry creation view"""
        response = self.client.post(
            reverse('create_inquiry'),
            {
                'property': self.property.pk,
                'inquiry_text': 'Test inquiry'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            PropertyInquiry.objects.filter(
                property=self.property,
                buyer=self.user_client
            ).exists()
        )

    def test_inquiry_list_view(self):
        """Test inquiry list view"""
        PropertyInquiry.objects.create(
            property=self.property,
            buyer=self.user_client,
            agent=self.employee,
            inquiry_text="Test inquiry"
        )
        response = self.client.get(reverse('inquiry_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inquiry_list.html')

    def test_inquiry_status_update(self):
        """Test inquiry status update"""
        inquiry = PropertyInquiry.objects.create(
            property=self.property,
            buyer=self.user_client,
            agent=self.employee,
            inquiry_text="Test inquiry"
        )
        response = self.client.post(
            reverse('update_inquiry_status', kwargs={'pk': inquiry.pk}),
            {'status': 'processing'}
        )
        self.assertEqual(response.status_code, 302)
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.state, 'processing')

