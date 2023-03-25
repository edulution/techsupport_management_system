from datetime import datetime
import uuid
from django.db import models
from allauth.socialaccount.models import SocialAccount


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Country(BaseModel):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=2)


class Region(BaseModel):
    name = models.CharField(max_length=30)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="regions"
    )


class Centre(BaseModel):
    name = models.CharField(max_length=30)
    acronym = models.CharField(max_length=5)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="centres")


class Category(BaseModel):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5)


class SubCategory(BaseModel):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="subcategories"
    )


class SupportTicket(BaseModel):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    )
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )

    date_submitted = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SupportTicket.Status.choices)
    priority = models.CharField(max_length=20, choices=SupportTicket.Priority.choices)
    centre = models.ForeignKey(
        Centre, on_delete=models.CASCADE, related_name="support_issues"
    )
    submitted_by = models.ForeignKey(
        SocialAccount, on_delete=models.CASCADE, related_name="submitted_issues"
    )
    resolved_by = models.ForeignKey(
        SocialAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="resolved_issues",
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="support_issues"
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="support_issues"
    )
    description = models.TextField(max_length=100, help_text="Describe the issue")

    def ticket_age(self):
        now = datetime.now()
        age = now - self.date_submitted
        return age
