from geopy.distance import geodesic

def is_within_radius(user_lat: float, user_lon: float, event_lat: float, event_lon: float, radius: float) -> bool:
    """
    Checks if a user is within a given radius from an event location.
    Uses the Haversine formula via geopy library.
    
    Args:
        user_lat: User's latitude
        user_lon: User's longitude
        event_lat: Event's latitude
        event_lon: Event's longitude
        radius: Allowed radius in meters
    
    Returns:
        bool: True if user is within radius, False otherwise
    """
    try:
        event_location = (event_lat, event_lon)
        user_location = (user_lat, user_lon)
        distance = geodesic(user_location, event_location).meters
        return distance <= radius
    except Exception as e:
        print(f"Error calculating distance: {str(e)}")
        return False
