# Generated by Django 3.0.7 on 2020-09-24 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0035_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('processed', 'Обработанный'), ('unprocessed', 'Необработанный')], default='unprocessed', max_length=11, verbose_name='Статус'),
        ),
    ]
