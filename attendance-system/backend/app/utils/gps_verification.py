from geopy.distance import geodesic
from typing import Dict, Any, Optional


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two GPS coordinates in meters."""
    try:
        point1 = (lat1, lng1)
        point2 = (lat2, lng2)
        return geodesic(point1, point2).meters
    except Exception:
        return float('inf')


def verify_location(
    student_lat: float, 
    student_lng: float, 
    session_lat: float, 
    session_lng: float, 
    allowed_radius: float = 100.0
) -> Dict[str, Any]:
    """Verify if student is within allowed radius of session location."""
    try:
        # Validate coordinates
        if not (-90 <= student_lat <= 90) or not (-180 <= student_lng <= 180):
            return {
                "is_valid": False,
                "distance_meters": None,
                "allowed_radius": allowed_radius,
                "error": "Invalid student coordinates",
                "error_detail": f"Student coordinates ({student_lat}, {student_lng}) are out of valid range"
            }
        
        if not (-90 <= session_lat <= 90) or not (-180 <= session_lng <= 180):
            return {
                "is_valid": False,
                "distance_meters": None,
                "allowed_radius": allowed_radius,
                "error": "Invalid session coordinates",
                "error_detail": f"Session coordinates ({session_lat}, {session_lng}) are out of valid range"
            }
        
        distance = calculate_distance(student_lat, student_lng, session_lat, session_lng)
        
        # Check for calculation errors
        if distance == float('inf'):
            return {
                "is_valid": False,
                "distance_meters": None,
                "allowed_radius": allowed_radius,
                "error": "Distance calculation failed",
                "error_detail": "Unable to calculate distance between coordinates"
            }
        
        is_within_range = distance <= allowed_radius
        
        return {
            "is_valid": is_within_range,
            "distance_meters": round(distance, 2),
            "allowed_radius": allowed_radius,
            "status": "within_range" if is_within_range else "too_far",
            "coordinates": {
                "student": {"lat": student_lat, "lng": student_lng},
                "session": {"lat": session_lat, "lng": session_lng}
            }
        }
    except Exception as e:
        return {
            "is_valid": False,
            "distance_meters": None,
            "allowed_radius": allowed_radius,
            "error": "Location verification error",
            "error_detail": str(e)
        }


def is_within_campus_bounds(lat: float, lng: float, campus_locations: Dict[str, Any]) -> bool:
    """Check if coordinates are within any allowed campus location."""
    try:
        for location_name, location_data in campus_locations.items():
            campus_lat = location_data.get("lat")
            campus_lng = location_data.get("lng")
            radius = location_data.get("radius", 500)
            
            if campus_lat and campus_lng:
                distance = calculate_distance(lat, lng, campus_lat, campus_lng)
                if distance <= radius:
                    return True
        return False
    except Exception:
        return False