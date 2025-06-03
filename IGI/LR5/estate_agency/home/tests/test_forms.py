import logging
from datetime import datetime

from django.test import TestCase
from django.conf import settings
from django.apps import apps
from ..forms import ReviewForm


class ReviewFormTest(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_form_fields(self):
        form = ReviewForm()
        self.assertEqual(list(form.fields.keys()), ["rating", "text"])

    def test_text_widget_attrs(self):
        form = ReviewForm()
        text_widget = form.fields["text"].widget
        self.assertEqual(text_widget.attrs["class"], "form-control")
        self.assertEqual(text_widget.attrs["rows"], 3)
        self.assertEqual(text_widget.attrs["placeholder"], "Ваш отзыв...")

    def test_rating_widget_attrs(self):
        form = ReviewForm()
        rating_widget = form.fields["rating"].widget
        self.assertEqual(rating_widget.attrs["class"], "form-select")

    def test_clean_long_text_valid(self):
        form_data = {
            "text": "Greater than 10 symbols.",
            "rating": 5,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_text_too_short(self):
        form_data = {
            "text": "Short",
            "rating": 5,
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["text"],
            ["Review text too short: less than 10 characters."],
        )

    def test_form_save(self):
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
        form_data = {
            "text": "Greater than 10 symbols.",
            "rating": 5,
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        review = form.save(commit=False)
        review.user = user
        review.save()
        self.assertEqual(review.text, form_data["text"])
        self.assertEqual(review.rating, form_data["rating"])
