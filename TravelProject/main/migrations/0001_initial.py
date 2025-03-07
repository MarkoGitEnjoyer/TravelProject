# Generated by Django 5.1.4 on 2025-02-28 20:44

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('GuideApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('trip_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('minimizedDescription', models.TextField(null=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='trip_images/')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('meeting_point', models.CharField(max_length=200)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('guide', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trips', to='GuideApp.guide')),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be numeric', regex='^[0-9]*$')])),
                ('email', models.EmailField(max_length=254)),
                ('id_number', models.CharField(max_length=20)),
                ('attended', models.BooleanField(default=False)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.trip')),
            ],
        ),
    ]
