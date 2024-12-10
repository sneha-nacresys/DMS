# Generated by Django 3.2 on 2024-11-22 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RouteMaster',
            fields=[
                ('RouteID', models.AutoField(primary_key=True, serialize=False)),
                ('StartLocation', models.CharField(max_length=255)),
                ('EndLocation', models.CharField(max_length=255)),
                ('OptimizedPath', models.JSONField()),
                ('EstimatedTime', models.DurationField()),
                ('ActualTime', models.DurationField(blank=True, null=True)),
                ('Distance', models.FloatField()),
                ('TrafficConditions', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'RouteMaster',
            },
        ),
        migrations.CreateModel(
            name='RouteOptimizationLogs',
            fields=[
                ('LogID', models.AutoField(primary_key=True, serialize=False)),
                ('DateGenerated', models.DateTimeField(auto_now_add=True)),
                ('AlgorithmUsed', models.CharField(blank=True, max_length=100)),
                ('TrafficDataUsed', models.JSONField(blank=True, null=True)),
                ('WeatherDataUsed', models.JSONField(blank=True, null=True)),
                ('AlternateRoutesConsidered', models.JSONField(blank=True, null=True)),
                ('Route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='routes.routemaster')),
            ],
            options={
                'db_table': 'RouteOptimizationLogs',
            },
        ),
    ]