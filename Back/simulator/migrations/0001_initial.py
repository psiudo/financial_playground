# Back/simulator/migrations/0001_initial.py
# Generated by Django 4.2.20 on 2025-05-26 00:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('strategies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualPortfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash_balance', models.BigIntegerField(default=10000000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VirtualTrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_type', models.CharField(choices=[('buy', '매수'), ('sell', '매도')], max_length=4)),
                ('stock_code', models.CharField(max_length=12)),
                ('stock_name', models.CharField(max_length=100)),
                ('price', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('traded_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='simulator.virtualportfolio')),
                ('strategy_run', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='strategies.strategyrun')),
            ],
            options={
                'ordering': ['-traded_at'],
            },
        ),
    ]
