# Generated by Django 4.2.2 on 2023-07-14 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('techsupport', '0005_alter_supportticket_centre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportticket',
            name='centre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='techsupport.centre'),
        ),
    ]
