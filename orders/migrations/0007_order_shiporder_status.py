# Generated by Django 4.1.4 on 2023-01-17 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_shiporder'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shiporder_status',
            field=models.CharField(default='New', max_length=50),
        ),
    ]
