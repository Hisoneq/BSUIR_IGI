from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import matplotlib.pyplot as plt
import os
import tempfile

from ..utils.statistics import StatisticsCalculator
from ..utils.plotter import Plotter
from ..models import Property, PropertyService, Transaction, PropertyInquiry
from users.models import CustomUser, Client, Employee

class StatisticsCalculatorTest(TestCase):
    """Test suite for StatisticsCalculator"""
    
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

    def test_property_stats(self):
        """Test property statistics calculation"""
        stats = StatisticsCalculator.get_property_stats()
        self.assertEqual(stats['total_properties'], 1)
        self.assertEqual(stats['active_listings'], 1)
        self.assertEqual(stats['avg_price'], Decimal('100000.00'))

    def test_transaction_stats(self):
        """Test transaction statistics calculation"""
        Transaction.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee
        )
        stats = StatisticsCalculator.get_transaction_stats()
        self.assertEqual(stats['total_transactions'], 1)
        self.assertEqual(stats['monthly_transactions'], 1)
        self.assertEqual(stats['avg_transaction_value'], Decimal('100100.00'))

    def test_service_performance(self):
        """Test service performance calculation"""
        Transaction.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee
        )
        performance = StatisticsCalculator.get_service_performance()
        self.assertEqual(len(performance), 1)
        self.assertEqual(performance[0]['total_transactions'], 1)
        self.assertEqual(performance[0]['total_revenue'], Decimal('100100.00'))

    def test_employee_performance(self):
        """Test employee performance calculation"""
        Transaction.objects.create(
            property=self.property,
            buyer=self.client,
            agent=self.employee
        )
        performance = StatisticsCalculator.get_employee_performance()
        self.assertEqual(len(performance), 1)
        self.assertEqual(performance[0]['total_sales'], 1)
        self.assertEqual(performance[0]['total_revenue'], Decimal('100100.00'))

class PlotterTest(TestCase):
    """Test suite for Plotter"""
    
    def setUp(self):
        self.plotter = Plotter()
        self.temp_dir = tempfile.mkdtemp()

    def test_plt_bars(self):
        """Test bar plot creation"""
        data = [1, 2, 3, 4, 5]
        categories = ['A', 'B', 'C', 'D', 'E']
        path = os.path.join(self.temp_dir, 'test_plot.png')
        
        self.plotter.plt_bars(
            data,
            path=path,
            categories=categories,
            x_label='X',
            y_label='Y',
            title='Test Plot'
        )
        
        self.assertTrue(os.path.exists(path))
        plt.close('all')

    def test_plt_bars_without_path(self):
        """Test bar plot creation without saving"""
        data = [1, 2, 3, 4, 5]
        categories = ['A', 'B', 'C', 'D', 'E']
        
        self.plotter.plt_bars(
            data,
            categories=categories,
            x_label='X',
            y_label='Y',
            title='Test Plot'
        )
        
        plt.close('all')

    def test_plt_bars_with_invalid_data(self):
        """Test bar plot creation with invalid data"""
        with self.assertRaises(ValueError):
            self.plotter.plt_bars([])
        plt.close('all')

    def tearDown(self):
        """Clean up temporary files"""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir) 