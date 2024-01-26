# Generated by Django 4.2.7 on 2023-11-16 02:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('techsupport', '0002_remove_supportticket_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportticket',
            name='archived',
        ),
        migrations.RemoveField(
            model_name='supportticket',
            name='date_archived',
        ),
        migrations.AddField(
            model_name='supportticket',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date created'),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]
