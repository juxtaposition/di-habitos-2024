# Generated by Django 5.1.2 on 2024-10-18 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habit', '0002_habit_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('hogar', 'hogar'), ('escuela', 'escuela'), ('trabajo', 'trabajo'), ('metas', 'metas'), ('otros', 'otros')], default='hogar', max_length=100)),
                ('color', models.CharField(default='#FF0000', max_length=25)),
            ],
        ),
        migrations.AlterField(
            model_name='habit',
            name='frequency',
            field=models.CharField(choices=[('diario', 'diario'), ('semanal', 'semanal'), ('mensual', 'mensual')], default='diario', max_length=50),
        ),
    ]
