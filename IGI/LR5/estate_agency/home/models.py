from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models


class AboutCompany(models.Model):
    text = models.TextField(help_text="Enter the company text")

    def __str__(self):
        return f"{self.text[:40]}..."


class News(models.Model):
    title = models.CharField(max_length=100)
    summary = models.TextField()
    image = models.ImageField(upload_to="news/", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ["-created"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.question


class Contact(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="contacts/")
    description = models.TextField()
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                message="Phone number must be +375(29)XXX-XX-XX",
                regex="^\\+375\\(29\\)\\d{3}-\\d{2}-\\d{2}$",
            )
        ],
    )
    email = models.EmailField()

    def __str__(self):
        return self.name


class Policy(models.Model):
    pass


class Vacancy(models.Model):
    position = models.CharField(max_length=100)
    salary = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.position


class Review(models.Model):
    RATING_CHOICES = [
        (1, "1 - Ужасно"),
        (2, "2 - Норм но не очень"),
        (3, "3 - Пойдет"),
        (4, "4 - Нормалик"),
        (5, "5 - Супер"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text[:40]}..."


class PromoCode(models.Model):
    code = models.CharField(max_length=50)
    discount = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    description = models.TextField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.code
