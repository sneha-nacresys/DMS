# In models.py of your Django app

from django.db import models

class RouteMaster(models.Model):
    RouteID = models.AutoField(primary_key=True)
    StartLocation = models.CharField(max_length=255)  # Can also store as JSON (latitude, longitude)
    EndLocation = models.CharField(max_length=255)    # Can also store as JSON (latitude, longitude)
    OptimizedPath = models.JSONField()                # Storing a list of waypoints in optimized order
    EstimatedTime = models.DurationField()            # Estimated time for the route
    ActualTime = models.DurationField(null=True, blank=True)  # Actual time after completion
    Distance = models.FloatField()                    # Total distance of the route in km
    TrafficConditions = models.TextField(null=True, blank=True)  # Text to store traffic-related info

    class Meta:
        db_table = 'RouteMaster'


class RouteOptimizationLogs(models.Model):
    LogID = models.AutoField(primary_key=True)
    Route = models.ForeignKey(RouteMaster, on_delete=models.CASCADE, related_name='logs')
    DateGenerated = models.DateTimeField(auto_now_add=True)   # Timestamp of when the route was generated
    AlgorithmUsed = models.CharField(max_length=100, blank=True)  # Name of the algorithm or "Google API"
    TrafficDataUsed = models.JSONField(null=True, blank=True)  # JSON to store traffic details
    WeatherDataUsed = models.JSONField(null=True, blank=True)  # JSON to store weather conditions
    AlternateRoutesConsidered = models.JSONField(null=True, blank=True)  # Store alternate routes data

    class Meta:
        db_table = 'RouteOptimizationLogs'
        
