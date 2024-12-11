from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import RouteMaster, RouteOptimizationLogs
import os
import requests
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
import json
# import google.auth
# from google.oauth2 import service_account

import re

def parse_duration(duration):
    if isinstance(duration, str):  # Check if it's a string like "117s"
        match = re.match(r"(\d+)s", duration)  # Extract seconds
        if match:
            return int(match.group(1))
    elif isinstance(duration, dict):  # Handle dictionary format if present
        return duration.get('seconds', 0)
    return 0  # Default to 0 if format is unexpected


class RouteOptimizationView(APIView):
    def post(self, request):
        # Load API key securely from environment variables
        # api_key = os.getenv("GOOGLE_API_KEY")
        api_key='AIzaSyAGU_QPzCeqFONmuNZPRukCB0HsKa1TrqY'
        print("---API KEY:---",api_key)
        # Extract start, end locations, and waypoints from the request data
        start_location = request.data.get("start_location")
        end_location = request.data.get("end_location")
        waypoints = request.data.get("waypoints", [])

        # Define Google Routes API URL with API key as a query parameter
        routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

        # Prepare request body for the Routes API
        body = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": start_location['latitude'],
                        "longitude": start_location['longitude']
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": end_location['latitude'],
                        "longitude": end_location['longitude']
                    }
                }
            },
            "intermediates": [
                {"location": {"latLng": {"latitude": wp['latitude'], "longitude": wp['longitude']}}} 
                for wp in waypoints
            ],
            "travelMode": "DRIVE",
            "computeAlternativeRoutes": False,  # Request alternative routes
            "routingPreference": "TRAFFIC_AWARE"  # Or "SHORTEST" or "BEST_ROUTE" 
        }
        print("------Body:-----",body)
        headers = {
            "Content-Type": "application/json",
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"  # Specify the fields to return
        }
        
        # Send the request to Google Routes API
        response = requests.post(routes_url, json=body, headers=headers)
        print("---Response:----",response)
        try:
            # Try to parse JSON data
            data = response.json()
            print("----Response data:-----", data)  # Debug print to check the structure of data
        except ValueError:
            # Handle non-JSON response
            return Response({"error": "Invalid response format from Google API. Expected JSON."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if 'routes' key exists in parsed JSON data
        if 'routes' not in data or not data['routes']:
            return Response({"error": "No routes found in the response."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare response data for all alternative routes
        response_data = []

        # Loop through all routes to extract distance, duration, and legs
        for route in data['routes']:
            # Extract total distance and convert it to kilometers
            total_distance = route.get('distanceMeters', 0) / 1000  # Convert meters to kilometers

            # Extract duration (in seconds) and convert to hours, minutes, seconds
            duration_data = route.get('duration', {})
            total_duration = duration_data.get('seconds', 0) if isinstance(duration_data, dict) else 0
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Extract legs for the route
            optimized_route = route.get('legs', [])
            legs_data = []

            for leg in optimized_route:
                # Parse duration
                leg_duration_seconds = parse_duration(leg.get('duration', {}))
                leg_hours, leg_remainder = divmod(leg_duration_seconds, 3600)
                leg_minutes, leg_seconds = divmod(leg_remainder, 60)

                # Parse distance
                leg_distance = leg.get('distanceMeters', 0) / 1000  # Convert to kilometers

                # Append detailed leg data
                legs_data.append({
                    "distance": leg_distance,
                    "duration": {
                        "hours": leg_hours,
                        "minutes": leg_minutes,
                        "seconds": leg_seconds
                    }
                })

            # Append route summary and legs data to response
            response_data.append({
                "optimized_route": optimized_route,
                "total_distance": total_distance,
                "estimated_time": {
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                },
                "legs": legs_data  # Include detailed leg data
            })

        # Return all alternative routes with detailed legs data
        return Response(response_data, status=status.HTTP_200_OK)




# class RouteOptimizationView(APIView):
#     def post(self, request):
#         # Load API key securely from environment variables
#         api_key = os.getenv("GOOGLE_API_KEY")
#         print("---API KEY:---",api_key)
#         # Extract start, end locations, and waypoints from the request data
#         start_location = request.data.get("start_location")
#         end_location = request.data.get("end_location")
#         waypoints = request.data.get("waypoints", [])

#         # Define Google Routes API URL with API key as a query parameter
#         routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

#         # Prepare request body for the Routes API
#         body = {
#             "origin": {
#                 "location": {
#                     "latLng": {
#                         "latitude": start_location['latitude'],
#                         "longitude": start_location['longitude']
#                     }
#                 }
#             },
#             "destination": {
#                 "location": {
#                     "latLng": {
#                         "latitude": end_location['latitude'],
#                         "longitude": end_location['longitude']
#                     }
#                 }
#             },
#             "intermediates": [
#                 {"location": {"latLng": {"latitude": wp['latitude'], "longitude": wp['longitude']}}} 
#                 for wp in waypoints
#             ],
#             "travelMode": "DRIVE",
#             "computeAlternativeRoutes": False,  # Request alternative routes
#             "routingPreference": "TRAFFIC_AWARE"  # Or "SHORTEST" or "BEST_ROUTE" 
#         }
#         print("------Body:-----",body)
#         headers = {
#             "Content-Type": "application/json",
#             "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"  # Specify the fields to return
#         }
        
#         # Send the request to Google Routes API
#         response = requests.post(routes_url, json=body, headers=headers)
#         print("---Response:----",response)
#         try:
#             # Try to parse JSON data
#             data = response.json()
#             print("----Response data:-----", data)  # Debug print to check the structure of data
#         except ValueError:
#             # Handle non-JSON response
#             return Response({"error": "Invalid response format from Google API. Expected JSON."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if 'routes' key exists in parsed JSON data
#         if 'routes' not in data or not data['routes']:
#             return Response({"error": "No routes found in the response."}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare response data for all alternative routes
#         response_data = []

#         # Loop through all routes to extract distance, duration, and legs
#         for route in data['routes']:
#             # Extract total distance and convert it to kilometers
#             total_distance = route.get('distanceMeters', 0) / 1000  # Convert meters to kilometers

#             # Extract duration (in seconds) and convert to hours, minutes, seconds
#             duration_data = route.get('duration', {})
#             total_duration = duration_data.get('seconds', 0) if isinstance(duration_data, dict) else 0
#             hours, remainder = divmod(total_duration, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             # Extract legs for the route
#             optimized_route = route.get('legs', [])
#             legs_data = []

#             for leg in optimized_route:
#                 # Extract distance for the leg and convert to kilometers
#                 leg_distance = leg.get('distanceMeters', 0) / 1000  # Convert meters to kilometers
                
#                 # Extract duration for the leg (in seconds) and convert to hours, minutes, seconds
#                 leg_duration_data = leg.get('duration', {})
#                 leg_total_duration = leg_duration_data.get('seconds', 0) if isinstance(leg_duration_data, dict) else 0
#                 leg_hours, leg_remainder = divmod(leg_total_duration, 3600)
#                 leg_minutes, leg_seconds = divmod(leg_remainder, 60)

#                 # Append detailed leg data
#                 legs_data.append({
#                     "distance": leg_distance,
#                     "duration": {
#                         "hours": leg_hours,
#                         "minutes": leg_minutes,
#                         "seconds": leg_seconds
#                     }
#                 })

#             # Append route summary and legs data to response
#             response_data.append({
#                 "optimized_route": optimized_route,
#                 "total_distance": total_distance,
#                 "estimated_time": {
#                     "hours": hours,
#                     "minutes": minutes,
#                     "seconds": seconds
#                 },
#                 "legs": legs_data  # Include detailed leg data
#             })

#         # Return all alternative routes with detailed legs data
#         return Response(response_data, status=status.HTTP_200_OK)



# working code with routes api
# class RouteOptimizationView(APIView):
#     def post(self, request):
#         # Load API key securely from environment variables
#         api_key = os.getenv("GOOGLE_API_KEY")
#         print("---API KEY:---",api_key)
#         # Extract start, end locations, and waypoints from the request data
#         start_location = request.data.get("start_location")
#         end_location = request.data.get("end_location")
#         waypoints = request.data.get("waypoints", [])

#         # Define Google Routes API URL with API key as a query parameter
#         routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

#         # Prepare request body for the Routes API
#         body = {
#             "origin": {
#                 "location": {
#                     "latLng": {
#                         "latitude": start_location['latitude'],
#                         "longitude": start_location['longitude']
#                     }
#                 }
#             },
#             "destination": {
#                 "location": {
#                     "latLng": {
#                         "latitude": end_location['latitude'],
#                         "longitude": end_location['longitude']
#                     }
#                 }
#             },
#             "intermediates": [
#                 {"location": {"latLng": {"latitude": wp['latitude'], "longitude": wp['longitude']}}} 
#                 for wp in waypoints
#             ],
#             "travelMode": "DRIVE",
#             "computeAlternativeRoutes": False,  # Request alternative routes
#             "routingPreference": "TRAFFIC_AWARE"  # Or "SHORTEST" or "BEST_ROUTE" 
#         }
#         print("------Body:-----",body)
#         headers = {
#             "Content-Type": "application/json",
#             "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"  # Specify the fields to return
#         }
        
#         # Send the request to Google Routes API
#         response = requests.post(routes_url, json=body, headers=headers)
#         print("---Response:----",response)
#         try:
#             # Try to parse JSON data
#             data = response.json()
#             print("----Response data:-----", data)  # Debug print to check the structure of data
#         except ValueError:
#             # Handle non-JSON response
#             return Response({"error": "Invalid response format from Google API. Expected JSON."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if 'routes' key exists in parsed JSON data
#         if 'routes' not in data or not data['routes']:
#             return Response({"error": "No routes found in the response."}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare response data for all alternative routes
#         response_data = []

#         # Loop through all routes to extract distance, duration, and legs
#         for route in data['routes']:
#             # Extract total distance and convert it to kilometers
#             total_distance = route.get('distanceMeters', 0) / 1000  # Convert meters to kilometers

#             # Extract duration (in seconds) and convert to hours, minutes, seconds
#             duration_data = route.get('duration', {})
#             total_duration = duration_data.get('seconds', 0) if isinstance(duration_data, dict) else 0
#             hours, remainder = divmod(total_duration, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             # Extract legs for the route
#             optimized_route = route.get('legs', [])

#             # Save route to the RouteMaster table
#             # route_instance = RouteMaster.objects.create(
#             #     StartLocation=json.dumps(start_location),
#             #     EndLocation=json.dumps(end_location),
#             #     OptimizedPath=optimized_route,
#             #     EstimatedTime=timedelta(hours=hours, minutes=minutes, seconds=seconds),
#             #     Distance=total_distance
#             # )

#             # Create a log entry in RouteOptimizationLogs
#             # RouteOptimizationLogs.objects.create(
#             #     Route=route_instance,
#             #     AlgorithmUsed="Google API",
#             #     TrafficDataUsed=json.dumps(data.get('trafficData', {})),  # Assuming traffic data is part of the response
#             #     AlternateRoutesConsidered=json.dumps(data.get('routes', []))  # Storing alternative routes
#             # )

#             # Append route details to response data
#             response_data.append({
#                 "optimized_route": optimized_route,
#                 "total_distance": total_distance,
#                 "estimated_time": {
#                     "hours": hours,
#                     "minutes": minutes,
#                     "seconds": seconds
#                 }
#             })

#         # Return all alternative routes
#         return Response(response_data, status=status.HTTP_200_OK)



# class RouteOptimizationView(APIView):
#     def post(self, request):
#         # Load API key securely from environment variables
#         api_key = os.getenv("GOOGLE_API_KEY")
#         print("---API KEY:---",api_key)
#         # Extract start, end locations, and waypoints from the request data
#         start_location = request.data.get("start_location")
#         end_location = request.data.get("end_location")
#         waypoints = request.data.get("waypoints", [])

#         # Define Google Routes API URL with API key as a query parameter
#         routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

#         # Prepare request body for the Routes API
#         body = {
#             "origin": {
#                 "location": {
#                     "latLng": {
#                         "latitude": start_location['latitude'],
#                         "longitude": start_location['longitude']
#                     }
#                 }
#             },
#             "destination": {
#                 "location": {
#                     "latLng": {
#                         "latitude": end_location['latitude'],
#                         "longitude": end_location['longitude']
#                     }
#                 }
#             },
#             "intermediates": [
#                 {"location": {"latLng": {"latitude": wp['latitude'], "longitude": wp['longitude']}}} 
#                 for wp in waypoints
#             ],
#             "travelMode": "DRIVE",
#             "computeAlternativeRoutes": False,  # Request alternative routes
#             "routingPreference": "TRAFFIC_AWARE"  # Or "SHORTEST" or "BEST_ROUTE" 
#         }
#         print("------Body:-----",body)
#         headers = {
#             "Content-Type": "application/json",
#             "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"  # Specify the fields to return
#         }
        
#         # Send the request to Google Routes API
#         response = requests.post(routes_url, json=body, headers=headers)
#         print("---Response:----",response)
#         try:
#             # Try to parse JSON data
#             data = response.json()
#             print("----Response data:-----", data)  # Debug print to check the structure of data
#         except ValueError:
#             # Handle non-JSON response
#             return Response({"error": "Invalid response format from Google API. Expected JSON."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if 'routes' key exists in parsed JSON data
#         if 'routes' not in data or not data['routes']:
#             return Response({"error": "No routes found in the response."}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare response data for all alternative routes
#         response_data = []

#         # Loop through all routes to extract distance, duration, and legs
#         # Loop through all routes to extract distance, duration, and legs
#         for route in data['routes']:
#             # Extract total distance and convert it to kilometers
#             total_distance = route.get('distanceMeters', 0) / 1000  # Convert meters to kilometers

#             # Extract duration (in seconds) and convert to hours, minutes, seconds
#             duration_data = route.get('duration', {})
#             total_duration = duration_data.get('seconds', 0) if isinstance(duration_data, dict) else 0
#             hours, remainder = divmod(total_duration, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             # Extract legs and remove `steps`
#             optimized_route = []
#             for leg in route.get('legs', []):
#                 leg_without_steps = {key: value for key, value in leg.items() if key != 'steps'}
#                 optimized_route.append(leg_without_steps)

#             # Append route details to response data
#             response_data.append({
#                 "optimized_route": optimized_route,
#                 "total_distance": total_distance,
#                 "estimated_time": {
#                     "hours": hours,
#                     "minutes": minutes,
#                     "seconds": seconds
#                 }
#             })
#         # Return all alternative routes
#         return Response(response_data, status=status.HTTP_200_OK)



# class RouteOptimizationView(APIView):
#     def post(self, request):
#         # Load API key securely from environment variables
#         api_key = os.getenv("GOOGLE_API_KEY")
#         print("---API KEY:---",api_key)
#         # Extract start, end locations, and waypoints from the request data
#         start_location = request.data.get("start_location")
#         end_location = request.data.get("end_location")
#         waypoints = request.data.get("waypoints", [])

#         # Define Google Routes API URL with API key as a query parameter
#         routes_url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

#         # Prepare request body for the Routes API
#         body = {
#             "origin": {
#                 "location": {
#                     "latLng": {
#                         "latitude": start_location['latitude'],
#                         "longitude": start_location['longitude']
#                     }
#                 }
#             },
#             "destination": {
#                 "location": {
#                     "latLng": {
#                         "latitude": end_location['latitude'],
#                         "longitude": end_location['longitude']
#                     }
#                 }
#             },
#             "intermediates": [
#                 {"location": {"latLng": {"latitude": wp['latitude'], "longitude": wp['longitude']}}} 
#                 for wp in waypoints
#             ],
#             "travelMode": "DRIVE",
#             "computeAlternativeRoutes": False,  # Request alternative routes
#             "routingPreference": "TRAFFIC_AWARE"  # Or "SHORTEST" or "BEST_ROUTE" 
#         }
#         print("------Body:-----",body)
#         headers = {
#             "Content-Type": "application/json",
#             "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs"  # Specify the fields to return
#         }
        
#         # Send the request to Google Routes API
#         response = requests.post(routes_url, json=body, headers=headers)
#         print("---Response:----",response)
#         try:
#             # Try to parse JSON data
#             data = response.json()
#             print("----Response data:-----", data)  # Debug print to check the structure of data
#         except ValueError:
#             # Handle non-JSON response
#             return Response({"error": "Invalid response format from Google API. Expected JSON."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if 'routes' key exists in parsed JSON data
#         if 'routes' not in data or not data['routes']:
#             return Response({"error": "No routes found in the response."}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare response data for all alternative routes
#         response_data = []

#         # Loop through all routes to extract distance, duration, and legs
#         for route in data['routes']:
#             # Extract total distance and convert it to kilometers
#             total_distance = route.get('distanceMeters', 0) / 1000  # Convert meters to kilometers

#             # Extract duration (in seconds) and convert to hours, minutes, seconds
#             duration_data = route.get('duration', {})
#             total_duration = duration_data.get('seconds', 0) if isinstance(duration_data, dict) else 0
#             hours, remainder = divmod(total_duration, 3600)
#             minutes, seconds = divmod(remainder, 60)

#             # Extract legs for the route
#             optimized_route = route.get('legs', [])

#             # Save route to the RouteMaster table
#             # route_instance = RouteMaster.objects.create(
#             #     StartLocation=json.dumps(start_location),
#             #     EndLocation=json.dumps(end_location),
#             #     OptimizedPath=optimized_route,
#             #     EstimatedTime=timedelta(hours=hours, minutes=minutes, seconds=seconds),
#             #     Distance=total_distance
#             # )

#             # Create a log entry in RouteOptimizationLogs
#             # RouteOptimizationLogs.objects.create(
#             #     Route=route_instance,
#             #     AlgorithmUsed="Google API",
#             #     TrafficDataUsed=json.dumps(data.get('trafficData', {})),  # Assuming traffic data is part of the response
#             #     AlternateRoutesConsidered=json.dumps(data.get('routes', []))  # Storing alternative routes
#             # )

#             # Append route details to response data
#             response_data.append({
#                 "optimized_route": optimized_route,
#                 "total_distance": total_distance,
#                 "estimated_time": {
#                     "hours": hours,
#                     "minutes": minutes,
#                     "seconds": seconds
#                 }
#             })

#         # Return all alternative routes
#         return Response(response_data, status=status.HTTP_200_OK)



