import unittest
from datetime import datetime

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
from users.models import Client, User
from ..views import (
    HomeView,
    AboutView,
    NewsListView,
    FAQListView,
    ContactListView,
    PolicyView,
    VacancyListView,
    PromoCodeView,
    ReviewListView,
    UpdateReviewView,
)
from ..models import (
    AboutCompany,
    FAQ,
    Vacancy,
    Contact,
    PromoCode,
    Review,
    News,
    Policy,
)
from ..forms import ReviewForm


class BaseViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            first_name="client",
            last_name="Test",
            role="client",
            phone_number="+375(29)777-77-77",
            birth_date=datetime(2000, 1, 1),
            username="client",
            password="testpass",
        )
        Client.objects.create(user=user)
        News.objects.create(title="Test News", summary="Content")
        AboutCompany.objects.create(text="About us")
        FAQ.objects.create(question="Test Q", answer="Test A")
        Vacancy.objects.create(
            position="Test Vacancy", description="Description", salary=1000
        )
        PromoCode.objects.create(
            code="TEST123", status=True, discount=10, description="Test Discount"
        )
        Review.objects.create(user=user, text="Test Review", rating=5)

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(pk=1)
        self.client = Client.objects.get(pk=1)
        self.news = News.objects.get(pk=1)
        self.about = AboutCompany.objects.get(pk=1)
        self.faq = FAQ.objects.get(pk=1)
        self.vacancy = Vacancy.objects.get(pk=1)
        self.promo = PromoCode.objects.get(pk=1)
        self.review = Review.objects.get(pk=1)

    def login(self):
        self.client.login(username="testuser", password="testpass")


class HomeViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_queryset(self):
        request = self.factory.get(reverse("home"))
        view = HomeView.as_view()
        response = view(request)
        self.assertEqual(response.context_data["last_news"], self.news)

    def test_get_queryset_no_news(self):
        News.objects.all().delete()
        request = self.factory.get(reverse("home"))
        view = HomeView.as_view()
        response = view(request)
        self.assertIsNone(response.context_data["last_news"])


class AboutViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_queryset(self):
        request = self.factory.get(reverse("about"))
        view = AboutView.as_view()
        response = view(request)
        self.assertEqual(response.context_data["about_info"], self.about)

    def test_get_queryset_no_about(self):
        AboutCompany.objects.all().delete()
        request = self.factory.get(reverse("about"))
        view = AboutView.as_view()
        response = view(request)
        self.assertIsNone(response.context_data["about_info"])


class NewsListViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_queryset(self):
        request = self.factory.get(reverse("news"))
        view = NewsListView.as_view()
        response = view(request)
        self.assertEqual(list(response.context_data["object_list"]), [self.news])

    def test_pagination(self):
        for i in range(10):
            News.objects.create(
                title=f"News {i}",
                summary="Content",
            )
        request = self.factory.get(reverse("news"), {"page": 2})
        view = NewsListView.as_view()
        response = view(request)
        self.assertEqual(len(response.context_data["object_list"]), 2)


class FAQListViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_queryset(self):
        request = self.factory.get(reverse("faq"))
        view = FAQListView.as_view()
        response = view(request)
        self.assertEqual(list(response.context_data["object_list"]), [self.faq])


class VacancyListViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_queryset(self):
        request = self.factory.get(reverse("vacancies"))
        view = VacancyListView.as_view()
        response = view(request)
        self.assertEqual(list(response.context_data["object_list"]), [self.vacancy])


class PromoCodeViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_context_data(self):
        inactive_promo = PromoCode.objects.create(
            code="INACTIVE", status=False, discount=10, description="Test Discount"
        )
        request = self.factory.get(reverse("promo-codes"))
        view = PromoCodeView.as_view()
        response = view(request)
        self.assertEqual(list(response.context_data["active_promos"]), [self.promo])
        self.assertEqual(
            list(response.context_data["archived_promos"]), [inactive_promo]
        )


class ReviewListViewTests(BaseViewTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    def test_get_context_data(self):
        request = self.factory.get(reverse("reviews"))
        view = ReviewListView.as_view()
        response = view(request)
        self.assertIsInstance(response.context_data["form"], ReviewForm)
        self.assertEqual(list(response.context_data["object_list"]), [self.review])

    def test_pagination(self):
        for i in range(11):
            Review.objects.create(user=self.user, text=f"Review {i}", rating=5)
        request = self.factory.get(reverse("reviews"), {"page": 2})
        view = ReviewListView.as_view()
        response = view(request)
        self.assertEqual(len(response.context_data["object_list"]), 2)
