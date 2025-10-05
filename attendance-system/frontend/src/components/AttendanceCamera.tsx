import React, { useRef, useCallback, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import Head from 'next/head';
import { getCurrentLocation, LocationData } from '../utils/geolocation';
import { apiClient } from '../utils/api';
import MapSelector from './MapSelector';

interface AttendanceCameraProps {
  sessionId: number;
  onSuccess: (message: string) => void;
  onError: (error: string) => void;
}

const AttendanceCamera: React.FC<AttendanceCameraProps> = ({
  sessionId,
  onSuccess,
  onError
}) => {
  const webcamRef = useRef<Webcam>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState<LocationData | null>(null);
  const [locationError, setLocationError] = useState('');
  const [showManualLocation, setShowManualLocation] = useState(false);
  const [manualCoords, setManualCoords] = useState({lat: '', lng: ''});

  const getLocation = useCallback(async () => {
    try {
      setLocationError('');
      const locationData = await getCurrentLocation();
      setLocation(locationData);
      return locationData;
    } catch (error: any) {
      setLocationError(error.message || 'Failed to get location');
      return null;
    }
  }, []);

  const useFUTALocation = useCallback(() => {
    const futaLocation = {
      latitude: 7.3000,
      longitude: 5.1450,
      accuracy: 0
    };
    setLocation(futaLocation);
    setLocationError('');
    return futaLocation;
  }, []);

  const useManualLocation = useCallback(() => {
    const lat = parseFloat(manualCoords.lat);
    const lng = parseFloat(manualCoords.lng);
    
    if (isNaN(lat) || isNaN(lng)) {
      setLocationError('Please enter valid coordinates');
      return null;
    }
    
    const manualLocation = {
      latitude: lat,
      longitude: lng,
      accuracy: 0
    };
    setLocation(manualLocation);
    setLocationError('');
    setShowManualLocation(false);
    return manualLocation;
  }, [manualCoords]);

  useEffect(() => {
    // Try to get location automatically when component mounts
    getLocation();
  }, []);

  const captureAndSubmit = useCallback(async () => {
    if (!webcamRef.current) {
      onError('Camera not available');
      return;
    }

    if (!location) {
      onError('Location is required. Please set your location first.');
      return;
    }

    setIsLoading(true);

    try {
      // Capture image
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        onError('Failed to capture image');
        setIsLoading(false);
        return;
      }

      console.log('Submitting attendance with data:', {
        session_id: sessionId,
        student_lat: location.latitude,
        student_lng: location.longitude,
        face_image_length: imageSrc.length
      });

      // Submit attendance
      const response = await apiClient.post('/attendance/mark', {
        session_id: sessionId,
        face_image_data: imageSrc,
        student_lat: location.latitude,
        student_lng: location.longitude
      });

      // Handle successful response
      const message = response.data?.message || 'Attendance marked successfully!';
      const verification = response.data?.verification;
      
      let detailedMessage = `✅ ${message}`;
      if (verification) {
        detailedMessage += `\n\n📊 Verification Details:`;
        detailedMessage += `\n👤 Face: ${verification.face_verified ? '✅ Verified' : '❌ Failed'}`;
        detailedMessage += `\n📍 Location: ${verification.location_verified ? '✅ Verified' : '❌ Failed'}`;
        if (verification.distance_meters !== undefined) {
          detailedMessage += ` (${Math.round(verification.distance_meters)}m from session)`;
        }
      }
      
      onSuccess(detailedMessage);
    } catch (error: any) {
      console.error('Attendance marking error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      let errorMessage = 'Failed to mark attendance';
      
      if (error.response?.data?.detail) {
        // Backend provides detailed error message
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Add status-specific context if no detailed message
      if (!error.response?.data?.detail) {
        if (error.response?.status === 400) {
          errorMessage = `❌ Verification Failed: ${errorMessage}`;
        } else if (error.response?.status === 401) {
          errorMessage = '❌ Authentication Error: Please log in again';
        } else if (error.response?.status === 403) {
          errorMessage = '❌ Access Denied: You do not have permission to mark attendance';
        } else if (error.response?.status === 404) {
          errorMessage = '❌ Session Error: Session not found or no longer active';
        } else if (error.response?.status === 500) {
          errorMessage = '❌ Server Error: Please try again in a moment';
        }
      }
      
      onError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, location, onSuccess, onError]);

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
          integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
          crossOrigin=""
        />
      </Head>
      <div className="space-y-6">
      {/* Location Setup */}
      {!location && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-4">Location Required</h3>
          
          {locationError && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{locationError}</p>
            </div>
          )}
          
          <MapSelector
            onLocationSelect={(lat, lng) => {
              const locationData = {
                latitude: lat,
                longitude: lng,
                accuracy: 0
              };
              setLocation(locationData);
              setLocationError('');
            }}
            height="250px"
          />
          
          <div className="flex space-x-2">
            <button
              onClick={getLocation}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              📱 My Location
            </button>
            
            <button
              onClick={useFUTALocation}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors"
            >
              🏫 FUTA Campus
            </button>
          </div>
        </div>
      )}
      
      {/* Camera and Attendance */}
      {location && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-xl p-4">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-600">📍 Location Ready</span>
            </div>
            <p className="text-sm text-gray-600">
              <strong>Coordinates:</strong> {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
              {location.accuracy > 0 && (
                <span className="block text-xs text-gray-500 mt-1">
                  Accuracy: ±{Math.round(location.accuracy)}m
                </span>
              )}
            </p>
            <button
              onClick={() => setLocation(null)}
              className="mt-2 text-sm text-blue-600 hover:text-blue-700 underline font-medium"
            >
              📍 Change Location
            </button>
          </div>
          
          <div className="text-center">
            <div className="relative inline-block">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="rounded-lg border-2 border-gray-300"
                videoConstraints={{
                  width: 640,
                  height: 480,
                  facingMode: 'user'
                }}
              />
            </div>
            
            <button
              onClick={captureAndSubmit}
              disabled={isLoading}
              className={`mt-4 px-8 py-3 rounded-xl font-semibold text-lg ${
                isLoading
                  ? 'bg-gray-400 cursor-not-allowed text-gray-600'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white transform hover:scale-105'
              } transition-all duration-200`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span>Verifying...</span>
                </div>
              ) : (
                '📸 Mark Attendance'
              )}
            </button>
            
            <div className="mt-3 text-xs text-gray-500 text-center">
              💡 Ensure good lighting and face the camera directly
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
};

export default AttendanceCamera;