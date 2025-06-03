import logging

from django import forms

from .models import Review

logger = logging.getLogger(__name__)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Напишите отзыв...",
                }
            ),
            "rating": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_text(self):
        text = self.cleaned_data["text"]
        logger.debug(f"Validating review text: length={len(text)}")
        if len(text) < 10:
            logger.error("Review text too short: less than 10 characters")
            raise forms.ValidationError(
                "Review text too short: less than 10 characters.)))"
            )
        logger.info("Review text validation passed")
        return text
