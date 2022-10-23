# Generated by Django 2.2.16 on 2022-10-23 15:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20221022_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(max_length=4, validators=[django.core.validators.MaxValueValidator(9999), django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Код цвета содержит недопустимый символ', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цвет в HEX'),
        ),
    ]
