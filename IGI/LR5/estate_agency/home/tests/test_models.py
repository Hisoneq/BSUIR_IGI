from django.apps import apps
from django.core.validators import MinValueValidator, MaxValueValidator
from django.test import TestCase
from django.conf import settings
from datetime import datetime, date
from ..models import (
    AboutCompany,
    News,
    FAQ,
    Contact,
    Vacancy,
    Review,
    PromoCode,
    Policy,
)


class AboutCompanyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        AboutCompany.objects.create(text="About Company")

    def setUp(self):
        self.about_company = AboutCompany.objects.get(pk=1)

    def test_text_label(self):
        field_label = self.about_company._meta.get_field("text").verbose_name
        self.assertEqual(field_label, "text")

    def text_text_help_text(self):
        help_text = self.about_company._meta.get_field("text").help_text
        self.assertEqual(help_text, "Enter the company text")

    def test_object_name_is_text_truncated(self):
        expected_object_name = f"{self.about_company.text[:40]}..."
        self.assertEqual(expected_object_name, str(self.about_company))


class NewsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.create(
            title="Test News",
            summary="This is a test news summary"
        )

    def setUp(self):
        self.news = News.objects.get(pk=1)

    def test_title_label(self):
        field_label = self.news._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        max_length = self.news._meta.get_field('title').max_length
        self.assertEqual(max_length, 100)

    def test_summary_label(self):
        field_label = self.news._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'summary')

    def test_meta_ordering(self):
        self.assertEqual(News._meta.ordering, ['-created'])

    def test_meta_verbose_names(self):
        self.assertEqual(News._meta.verbose_name, 'News')
        self.assertEqual(News._meta.verbose_name_plural, 'News')

    def test_object_name_is_title(self):
        self.assertEqual(str(self.news), self.news.title)


class FAQModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        FAQ.objects.create(
            question="Test Question",
            answer="Test Answer",
            added_date=date.today()
        )

    def setUp(self):
        self.faq = FAQ.objects.get(pk=1)

    def test_question_label(self):
        field_label = self.faq._meta.get_field('question').verbose_name
        self.assertEqual(field_label, 'question')

    def test_question_max_length(self):
        max_length = self.faq._meta.get_field('question').max_length
        self.assertEqual(max_length, 100)

    def test_answer_label(self):
        field_label = self.faq._meta.get_field('answer').verbose_name
        self.assertEqual(field_label, 'answer')

    def test_added_date_label(self):
        field_label = self.faq._meta.get_field('added_date').verbose_name
        self.assertEqual(field_label, 'added date')

    def test_object_name_is_question(self):
        self.assertEqual(str(self.faq), self.faq.question)


class ContactModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Contact.objects.create(
            name="Test Contact",
            position="Test Position",
            description="Test Description",
            phone="+375(29)123-45-67",
            email="test@example.com"
        )

    def setUp(self):
        self.contact = Contact.objects.get(pk=1)

    def test_name_label(self):
        field_label = self.contact._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_position_label(self):
        field_label = self.contact._meta.get_field('position').verbose_name
        self.assertEqual(field_label, 'position')

    def test_photo_label(self):
        field_label = self.contact._meta.get_field('photo').verbose_name
        self.assertEqual(field_label, 'photo')

    def test_description_label(self):
        field_label = self.contact._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_phone_label(self):
        field_label = self.contact._meta.get_field('phone').verbose_name
        self.assertEqual(field_label, 'phone')

    def test_email_label(self):
        field_label = self.contact._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')

    def test_name_max_length(self):
        max_length = self.contact._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    def test_position_max_length(self):
        max_length = self.contact._meta.get_field('position').max_length
        self.assertEqual(max_length, 100)

    def test_phone_max_length(self):
        max_length = self.contact._meta.get_field('phone').max_length
        self.assertEqual(max_length, 20)

    def test_object_name_is_name(self):
        self.assertEqual(str(self.contact), self.contact.name)


class VacancyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Vacancy.objects.create(
            position="Test Position",
            salary=1000,
            description="Test Description"
        )

    def setUp(self):
        self.vacancy = Vacancy.objects.get(pk=1)

    def test_position_label(self):
        field_label = self.vacancy._meta.get_field('position').verbose_name
        self.assertEqual(field_label, 'position')

    def test_salary_label(self):
        field_label = self.vacancy._meta.get_field('salary').verbose_name
        self.assertEqual(field_label, 'salary')

    def test_description_label(self):
        field_label = self.vacancy._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_position_max_length(self):
        max_length = self.vacancy._meta.get_field('position').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_position(self):
        self.assertEqual(str(self.vacancy), self.vacancy.position)


class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = apps.get_model(settings.AUTH_USER_MODEL)

        user = User.objects.create_user(
            first_name="Employee",
            last_name="Test",
            role="employee",
            phone_number="+375(29)777-77-77",
            birth_date=datetime(2000, 1, 1),
            username="employee_test",
            password="<PASSWORD>",
        )
        Review.objects.create(
            user=user,
            rating=5,
            text="This is a test review"
        )

    def setUp(self):
        self.review = Review.objects.get(pk=1)

    def test_user_label(self):
        field_label = self.review._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_rating_label(self):
        field_label = self.review._meta.get_field('rating').verbose_name
        self.assertEqual(field_label, 'rating')

    def test_text_label(self):
        field_label = self.review._meta.get_field('text').verbose_name
        self.assertEqual(field_label, 'text')

    def test_created_at_label(self):
        field_label = self.review._meta.get_field('created_at').verbose_name
        self.assertEqual(field_label, 'created at')

    def test_updated_at_label(self):
        field_label = self.review._meta.get_field('updated_at').verbose_name
        self.assertEqual(field_label, 'updated at')

    def test_rating_choices(self):
        rating_choices = self.review._meta.get_field('rating').choices
        expected_choices = Review.RATING_CHOICES
        self.assertEqual(rating_choices, expected_choices)

    def test_rating_default(self):
        self.assertEqual(self.review.rating, 5)

    def test_object_name_is_text_truncated(self):
        expected_object_name = f"{self.review.text[:40]}..."
        self.assertEqual(expected_object_name, str(self.review))


class PromoCodeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        PromoCode.objects.create(
            code="TESTCODE",
            discount=10,
            description="Test promo code"
        )

    def setUp(self):
        self.promo = PromoCode.objects.get(pk=1)

    def test_code_label(self):
        field_label = self.promo._meta.get_field('code').verbose_name
        self.assertEqual(field_label, 'code')

    def test_discount_label(self):
        field_label = self.promo._meta.get_field('discount').verbose_name
        self.assertEqual(field_label, 'discount')

    def test_description_label(self):
        field_label = self.promo._meta.get_field('description').verbose_name
        self.assertEqual(field_label, 'description')

    def test_status_label(self):
        field_label = self.promo._meta.get_field('status').verbose_name
        self.assertEqual(field_label, 'status')

    def test_code_max_length(self):
        max_length = self.promo._meta.get_field('code').max_length
        self.assertEqual(max_length, 50)

    def test_discount_validators(self):
        validators = self.promo._meta.get_field('discount').validators
        self.assertTrue(any(isinstance(v, MinValueValidator) and v.limit_value == 1 for v in validators))
        self.assertTrue(any(isinstance(v, MaxValueValidator) and v.limit_value == 100 for v in validators))

    def test_status_default(self):
        self.assertTrue(self.promo.status)

    def test_object_name_is_code(self):
        self.assertEqual(str(self.promo), self.promo.code)
