# Generated by Django 3.0 on 2019-12-07 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bday',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bday', models.DateField(verbose_name='Дата')),
                ('man', models.CharField(max_length=50, verbose_name='Именинник')),
                ('comment', models.CharField(blank=True, max_length=50, null=True, verbose_name='Комментарий')),
            ],
        ),
    ]
