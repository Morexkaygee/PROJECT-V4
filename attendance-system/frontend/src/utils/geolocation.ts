export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
}

export interface LocationError {
  code: number;
  message: string;
}

export const getCurrentLocation = (): Promise<LocationData> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject({
        code: 0,
        message: 'Geolocation is not supported by this browser'
      });
      return;
    }

    const options = {
      enableHighAccuracy: false,
      timeout: 15000,
      maximumAge: 300000
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        let message = 'Unknown location error';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = 'Please allow location access in your browser settings';
            break;
          case error.POSITION_UNAVAILABLE:
            message = 'Location services unavailable. Please check your device settings';
            break;
          case error.TIMEOUT:
            message = 'Location request timed out. Please try again';
            break;
          default:
            message = `Location error (${error.code}): ${error.message || 'Please enable location services'}`;
        }
        
        reject({
          code: error.code,
          message
        });
      },
      options
    );
  });
};

export const calculateDistance = (
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number => {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // Distance in meters
};