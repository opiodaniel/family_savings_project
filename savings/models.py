from django.conf import settings
from django.db import models
from django.utils import timezone


# 1. Member Model (Updated with Location and Phone fields)
class Member(models.Model):
    # Required Profile Details
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    current_location = models.CharField(max_length=255, verbose_name="Current Location")

    # Phone fields (PhoneNum1 required, PhoneNum2 optional)
    phone_number_1 = models.CharField(max_length=20, verbose_name="Primary Phone")
    phone_number_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Secondary Phone")

    # Link to Django User for Authentication
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username if self.user else 'No User'})"


# 2. Contribution Model
class Contribution(models.Model):
    member = models.ForeignKey(Member, related_name="contributions", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    month = models.PositiveSmallIntegerField(editable=False)  # Handled in save method
    year = models.PositiveSmallIntegerField(editable=False)  # Handled in save method
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # **Handles the one-contribution-per-month logic**
        # Database constraint ensures member can only have one entry for a given month and year.
        unique_together = ('member', 'month', 'year')
        ordering = ['-year', '-month', '-created_at']

    def save(self, *args, **kwargs):
        # Automatically populate month and year from the date field
        self.month = self.date.month
        self.year = self.date.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member} - {self.month}/{self.year}: {self.amount}"


# 3. Expense Model
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('wedding', 'Wedding support'),
        ('burial', 'Burial support'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"
