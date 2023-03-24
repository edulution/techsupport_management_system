import uuid
from django.db import models


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
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10)
    priority = models.CharField(max_length=10)
    centre = models.ForeignKey(
        Centre, on_delete=models.CASCADE, related_name="support_issues"
    )
    # submitted_by = models.ForeignKey(auth, on_delete=models.CASCADE, related_name='submitted_issues')
    # resolved_by = models.ForeignKey(auth, on_delete=models.CASCADE, null=True, blank=True, related_name='resolved_issues')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="support_issues"
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="support_issues"
    )
    description = models.TextField(max_length=100, help_text="Describe the issue")
