# Generated by Django 2.2.16 on 2022-10-22 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20221022_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('#0000FF', 'Синий'), ('#FFA500', 'Оранжевый'), ('#008000', 'Зеленый'), ('#800080', 'Фиолетовый'), ('#FFD700', 'Желтый'), ('#8B0000', 'Красный'), ('#808080', 'Серый')], max_length=7, unique=True, verbose_name='Цвет в HEX'),
        ),
    ]
