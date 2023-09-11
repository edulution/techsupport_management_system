# Generated by Django 3.2.18 on 2023-08-29 14:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('techsupport', '0012_alter_supportticket_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AddField(
            model_name='settings',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='settings_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='settings',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userprofile_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='category',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='centre',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='centre',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='country',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='country',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='country_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='country',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='region',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='region',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='region_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='region',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='date_submitted',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date submitted'),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]
