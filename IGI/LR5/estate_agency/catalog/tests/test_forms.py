from django.test import SimpleTestCase
from ..forms import PropertyInquiryForm

class InquiryFormFieldTests(SimpleTestCase):
    def setUp(self):
        self.form = PropertyInquiryForm()

    def test_inquiry_text_field_exists(self):
        self.assertIn('inquiry_text', self.form.fields)

    def test_inquiry_text_label_is_empty(self):
        self.assertEqual(self.form.fields['inquiry_text'].label, '')

    def test_inquiry_textarea_widget(self):
        widget = self.form.fields['inquiry_text'].widget
        self.assertEqual(widget.attrs.get('rows'), 3)
        self.assertIn('placeholder', widget.attrs)
        self.assertTrue(widget.attrs['placeholder'].startswith('Опишите'))
        self.assertEqual(widget.__class__.__name__, 'Textarea')

    def test_valid_data(self):
        valid = PropertyInquiryForm(data={'inquiry_text': 'Что-то интересует'})
        self.assertTrue(valid.is_valid())

    def test_empty_inquiry_text_is_valid(self):
        empty = PropertyInquiryForm(data={'inquiry_text': ''})
        self.assertTrue(empty.is_valid())
