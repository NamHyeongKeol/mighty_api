# Generated by Django 2.2 on 2019-04-21 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mighty', '0004_auto_20190420_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='suit',
            field=models.CharField(choices=[('spade', 'spade'), ('diamond', 'diamond'), ('clover', 'clover'), ('heart', 'heart'), ('Joker', 'Joker')], db_index=True, max_length=10),
        ),
    ]
