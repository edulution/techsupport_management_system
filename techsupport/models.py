from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from allauth.socialaccount.models import SocialAccount
from smart_selects.db_fields import ChainedForeignKey
import uuid


class BaseModel(models.Model):
    """Abstract base model with UUID primary key."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("date created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("date modified"))
    modified_by = models.ForeignKey(
        SocialAccount,
        verbose_name=_("modified by"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Role(BaseModel):
    """Model representing user role."""

    class RoleType(models.TextChoices):
        ADMIN = "admin", _("Admin")
        MANAGER = "manager", _("Manager")
        TECHNICIAN = "technician", _("Technician")
        USER = "user", _("User")

    kind = models.CharField(
        max_length=30, verbose_name=_("kind"), choices=RoleType.choices
    )

    class Meta:
        verbose_name = "role"
        verbose_name_plural = "roles"


class RolePermissionMixin:
    """Mixin to define custom permissions for each role."""

    # Define permissions for each role as a class attribute
    PERMISSIONS = {
        Role.RoleType.ADMIN: {
            "can_filter": _("Can filter admins"),
            "can_delete": _("Can delete admins"),
            "can_update": _("Can update admins"),
            "can_read": _("Can read admins"),
            "can_create": _("Can create admins"),
        },
        Role.RoleType.MANAGER: {
            "can_filter": _("Can filter managers"),
            "can_delete": _("Can delete managers"),
            "can_update": _("Can update managers"),
            "can_read": _("Can read managers"),
            "can_create": _("Can create managers"),
        },
        Role.RoleType.TECHNICIAN: {
            "can_filter": _("Can filter technicians"),
            "can_delete": _("Can delete technicians"),
            "can_update": _("Can update technicians"),
            "can_read": _("Can read technicians"),
            "can_create": _("Can create technicians"),
        },
        Role.RoleType.USER: {
            "can_filter": _("Can filter users"),
            "can_delete": _("Can delete users"),
            "can_update": _("Can update users"),
            "can_read": _("Can read users"),
            "can_create": _("Can create users"),
        },
    }

    def _get_permission_codename(self, permission_name):
        """Get the permission codename."""
        return f"{self.__class__.__name__.lower()}_{permission_name}"

    def get_role_permissions(self):
        """Get permissions for the user's role."""
        try:
            role = Role.objects.get(kind=self.user.role)
        except Role.DoesNotExist:
            return []
        permissions = self.PERMISSIONS.get(role.kind, {})
        return [
            Permission.objects.get(codename=self._get_permission_codename(p))
            for p in permissions.keys()
        ]

    def has_perm(self, perm, obj=None):
        """Check if the user has the specified permission."""
        if self.is_superuser:
            return True
        if not self.is_active:
            return False
        if perm in self.get_role_permissions():
            return True
        return super().has_perm(perm, obj=obj)


class CustomSocialAccount(RolePermissionMixin, SocialAccount):
    """SocialAccount model extended with custom permissions."""


class Country(BaseModel):
    """Model representing a country."""

    name = models.CharField(max_length=30, verbose_name=_("name"))
    code = models.CharField(max_length=2, verbose_name=_("code"))

    def __str__(self):
        return f"{self.code}:{self.name}"

    class Meta:
        verbose_name_plural = "countries"


class Region(BaseModel):
    """Model representing a region within a country."""

    name = models.CharField(max_length=30, verbose_name=_("name"))
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="regions",
        verbose_name=_("country"),
    )

    def __str__(self):
        return f"{self.country.code}:{self.name}"

    class Meta:
        verbose_name_plural = "regions"


class Centre(BaseModel):
    """Model representing a support centre within a region."""

    name = models.CharField(max_length=30, verbose_name=_("name"))
    acronym = models.CharField(max_length=5, verbose_name=_("acronym"))
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="centres",
        verbose_name=_("region"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "centres"


class Category(BaseModel):
    """Model representing a category of support issues."""

    name = models.CharField(max_length=30, verbose_name=_("name"))
    code = models.CharField(max_length=5, verbose_name=_("code"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class SubCategory(BaseModel):
    """Model representing a subcategory of support issues within a category."""

    name = models.CharField(max_length=30, verbose_name=_("name"))
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="subcategories",
        verbose_name=_("category"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "subcategories"


class SupportTicket(BaseModel):
    """Model representing a support ticket submitted by a coach."""

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")

    ticket_number = models.PositiveIntegerField(
        verbose_name=_("ticket number"), unique=True, editable=False
    )
    date_submitted = models.DateTimeField(
        verbose_name=_("date submitted"), auto_now_add=True
    )
    date_resolved = models.DateTimeField(
        verbose_name=_("date resolved"), null=True, blank=True
    )
    status = models.CharField(
        max_length=30, verbose_name=_("status"), choices=Status.choices
    )
    priority = models.CharField(
        max_length=30, verbose_name=_("priority"), choices=Priority.choices
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
    title = models.CharField(
        verbose_name=_("title"),
        max_length=20,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        """
        Override the save method to set the ticket number and support description.

        Args:
            *args: Arguments passed to the superclass method.
            **kwargs: Keyword arguments passed to the superclass method.
        """
        if not self.ticket_number:
            max_ticket_number = SupportTicket.objects.aggregate(
                max_ticket_number=models.Max("ticket_number")
            )["max_ticket_number"]
            self.ticket_number = (max_ticket_number or 0) + 1

        if not self.title:
            self.title = f"{self.ticket_number}-{self.category.code}-{self.subcategory.code}-{self.description[:20]}"
        super().save(*args, **kwargs)

    def ticket_age(self):
        """
        Method that returns the difference between the current time and the time
        the support ticket was submitted.
        """
        now = timezone.now()
        age = now - self.date_submitted
        return age
