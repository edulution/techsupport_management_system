# Generated by Django 4.2.2 on 2023-07-13 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('techsupport', '0003_user_centres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportticket',
            name='description',
            field=models.TextField(help_text='Describe the issue', max_length=100, verbose_name='description'),
        ),
    ]
