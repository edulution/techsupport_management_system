# Generated by Django 4.2.2 on 2023-07-14 14:47

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('techsupport', '0004_alter_supportticket_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportticket',
            name='centre',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='name', chained_model_field='name', on_delete=django.db.models.deletion.CASCADE, related_name='support_issues', to='techsupport.centre', verbose_name='centre'),
        ),
    ]
