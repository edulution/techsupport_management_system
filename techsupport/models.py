from django.utils import timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
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
    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")

    date_submitted = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=SupportTicket.Status.choices)
    priority = models.CharField(choices=SupportTicket.Priority.choices)
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
        now = timezone.now()
        age = now - self.date_submitted
        return age
