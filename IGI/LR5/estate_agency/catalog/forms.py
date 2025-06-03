from django import forms
import logging

from .models import PropertyInquiry, PropertyType

logger = logging.getLogger(__name__)

class PropertyInquiryForm(forms.ModelForm):
    class Meta:
        model = PropertyInquiry
        fields = ['inquiry_text']
        labels = {
            'inquiry_text': ''
        }
        widgets = {
            'inquiry_text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Опишите ваши требования и вопросы...'
            }),
        }

class PropertyForm(forms.ModelForm):
    class Meta:
        model = PropertyType
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Опишите тип недвижимости...'
            }),
        }
