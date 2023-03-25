from django.utils import timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from allauth.socialaccount.models import SocialAccount
from smart_selects.db_fields import ChainedForeignKey


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class Country(BaseModel):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    code = models.CharField(max_length=2, verbose_name=_("code"))


class Region(BaseModel):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="regions",
        verbose_name=_("country"),
    )


class Centre(BaseModel):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    acronym = models.CharField(max_length=5, verbose_name=_("acronym"))
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="centres",
        verbose_name=_("region"),
    )


class Category(BaseModel):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    code = models.CharField(max_length=5, verbose_name=_("code"))


class SubCategory(BaseModel):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="subcategories",
        verbose_name=_("category"),
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

    date_submitted = models.DateTimeField(
        verbose_name=_("date submitted"), auto_now_add=True
    )
    date_resolved = models.DateTimeField(
        verbose_name=_("date resolved"), null=True, blank=True
    )
    status = models.CharField(
        verbose_name=_("status"), choices=SupportTicket.Status.choices, max_length=20
    )
    priority = models.CharField(
        verbose_name=_("priority"),
        choices=SupportTicket.Priority.choices,
        max_length=20,
    )
    centre = ChainedForeignKey(
        Centre,
        chained_field="region",
        chained_model_field="region",
        show_all=False,
        auto_choose=True,
        verbose_name=_("centre"),
        on_delete=models.CASCADE,
        related_name="support_issues",
    )
    submitted_by = models.ForeignKey(
        SocialAccount,
        verbose_name=_("submitted by"),
        on_delete=models.CASCADE,
        related_name="submitted_issues",
    )
    resolved_by = models.ForeignKey(
        SocialAccount,
        verbose_name=_("resolved by"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="resolved_issues",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        on_delete=models.CASCADE,
        related_name="support_issues",
    )
    subcategory = ChainedForeignKey(
        SubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        verbose_name=_("subcategory"),
        on_delete=models.CASCADE,
        related_name="support_issues",
    )
    description = models.TextField(
        verbose_name=_("description"),
        help_text="Describe the issue",
    )

    def ticket_age(self):
        now = timezone.now()
        age = now - self.date_submitted
        return age
