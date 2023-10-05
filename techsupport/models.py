from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Permission, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from smart_selects.db_fields import ChainedForeignKey
import uuid

# from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError


class RolePermissionMixin:
    """Mixin to define custom permissions for each role."""

    PERMISSIONS = {
        "admin": {
            "can_filter": _("Can filter admins"),
            "can_delete": _("Can delete admins"),
            "can_update": _("Can update admins"),
            "can_read": _("Can read admins"),
            "can_create": _("Can create admins"),
        },
        "manager": {
            "can_read": _("Can read managers"),
            "can_create": _("Can create managers"),
        },
        "technician": {
            "can_filter": _("Can filter technicians"),
            "can_update": _("Can update technicians"),
            "can_read": _("Can read technicians"),
        },
        "user": {
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
            role = self.role
        except AttributeError:
            return []
        permissions = self.PERMISSIONS.get(role, {})
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


class BaseModel(models.Model):
    """Abstract base model with UUID primary key."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(
        default=now, editable=False, verbose_name=_("date created")
    )
    updated_at = models.DateTimeField(
        default=now, editable=False, verbose_name=_("date modified")
    )
    modified_by = models.ForeignKey(
        "User",
        verbose_name=_("modified by"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_modified",
    )

    class Meta:
        abstract = True


class Country(BaseModel):
    """Model representing a country."""

    name = models.CharField(max_length=30, verbose_name=_("name"), unique=True)
    code = models.CharField(max_length=2, verbose_name=_("code"), unique=True)

    def __str__(self):
        return f"{self.code}:{self.name}"

    class Meta:
        verbose_name_plural = "countries"


class Region(BaseModel):
    """Model representing a region within a country."""

    name = models.CharField(max_length=30, verbose_name=_("name"), unique=True)
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

    name = models.CharField(max_length=30, verbose_name=_("name"), unique=True)
    acronym = models.CharField(max_length=5, verbose_name=_("acronym"), unique=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="centres",
        verbose_name=_("region"),
    )

    def __str__(self):
        return f"{self.acronym} - {self.name}"

    class Meta:
        verbose_name_plural = "centres"


class User(AbstractUser, RolePermissionMixin):
    """Custom user model that inherits from AbstractUser model"""

    class RoleType(models.TextChoices):
        SUPER_ADMIN = "super_admin", _("Super Admin")
        ADMIN = "admin", _("Admin")
        MANAGER = "manager", _("Manager")
        TECHNICIAN = "technician", _("Technician")
        USER = "user", _("User")

    ROLE_HIERARCHY = {
        RoleType.SUPER_ADMIN: [RoleType.ADMIN],
        RoleType.ADMIN: [RoleType.TECHNICIAN, RoleType.MANAGER, RoleType.USER],
        RoleType.MANAGER: [RoleType.TECHNICIAN, RoleType.USER],
        RoleType.TECHNICIAN: [RoleType.USER],
        RoleType.USER: [],
    }

    role = models.CharField(
        max_length=30,
        verbose_name=_("role"),
        choices=RoleType.choices,
        default=RoleType.USER,
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        verbose_name=_("country"),
        null=True,
        blank=True,
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        verbose_name=_("region"),
        null=True,
        blank=True,
    )

    def is_super_admin(self):
        """Check if the user is a super admin."""
        return self.role == self.RoleType.SUPER_ADMIN

    def is_admin(self):
        """Check if the user is an admin or a super admin."""
        return self.role in [self.RoleType.ADMIN, self.RoleType.SUPER_ADMIN]

    def is_manager(self):
        """Check if the user is a manager or higher role."""
        return self.role in [
            self.RoleType.MANAGER,
            self.RoleType.ADMIN,
            self.RoleType.SUPER_ADMIN,
        ]

    def is_technician(self):
        """Check if the user is a technician or higher role."""
        return self.role in [
            self.RoleType.TECHNICIAN,
            self.RoleType.MANAGER,
            self.RoleType.ADMIN,
            self.RoleType.SUPER_ADMIN,
        ]

    def is_user(self):
        """Check if the user is a user or higher role."""
        return self.role in [
            self.RoleType.USER,
            self.RoleType.TECHNICIAN,
            self.RoleType.MANAGER,
            self.RoleType.ADMIN,
            self.RoleType.SUPER_ADMIN,
        ]

    centres = models.ManyToManyField(Centre, related_name="users")


def save(self, *args, **kwargs):
    if not self.pk:
        for role in self.ROLE_HIERARCHY.get(self.role, []):
            if User.objects.filter(role=role).exists():
                raise ValidationError(
                    f"A {role} already exists. Cannot assign the {self.role} role."
                )

    if self.role == self.RoleType.USER and not self.centres.exists():
        raise ValidationError("A user must belong to at least one centre.")

    super(User, self).save(*args, **kwargs)


class UserProfile(BaseModel):
    """Model representing a user profile."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(verbose_name=_("biography"), blank=True)
    avatar = models.ImageField(
        verbose_name=_("avatar"), upload_to="avatars/", blank=True
    )
    date_of_birth = models.DateField(
        verbose_name=_("date of birth"), null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)


class Settings(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Category(BaseModel):
    """Model representing a category of support issues."""

    name = models.CharField(max_length=30, verbose_name=_("name"), unique=True)
    code = models.CharField(max_length=5, verbose_name=_("code"), unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class SubCategory(BaseModel):
    """Model representing a subcategory of support issues within a category."""

    name = models.CharField(max_length=30, verbose_name=_("name"), unique=True)
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
        OPEN = "Open", _("Open")
        IN_PROGRESS = "In Progress", _("In Progress")
        RESOLVED = "Resolved", _("Resolved")
        CLOSED = "Closed", _("Closed")

    class Priority(models.TextChoices):
        LOW = "Low", _("Low")
        MEDIUM = "Medium", _("Medium")
        HIGH = "High", _("High")

    ticket_number = models.PositiveIntegerField(
        verbose_name=_("ticket number"), unique=True, editable=False
    )
    date_submitted = models.DateTimeField(
        verbose_name=_("date submitted"), default=now, editable=False
    )
    date_resolved = models.DateTimeField(
        verbose_name=_("date resolved"), null=True, blank=True
    )
    status = models.CharField(
        max_length=30, verbose_name=_("status"), choices=Status.choices
    )
    priority = models.CharField(
        max_length=30,
        verbose_name=_("priority"),
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    centre = models.ForeignKey(
        Centre,
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    submitted_by = models.ForeignKey(
        User,
        verbose_name=_("submitted by"),
        on_delete=models.CASCADE,
        related_name="submitted_issues",
    )
    resolved_by = models.ForeignKey(
        User,
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
        max_length=100,
        help_text="Describe the issue",
    )
    title = models.CharField(
        verbose_name=_("title"),
        max_length=20,
        null=True,
        blank=True,
    )
    resolution_notes = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        User,
        verbose_name=_("assigned to"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
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

        if age.days >= 1:
            days = age.days
            hours, remainder = divmod(age.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            if hours > 0:
                return f"{days} days ago"
            else:
                return f"{days} days ago"
        else:
            hours, remainder = divmod(age.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            if hours > 0:
                return f"{hours} hrs ago"
            else:
                return f"{minutes} mins ago"
