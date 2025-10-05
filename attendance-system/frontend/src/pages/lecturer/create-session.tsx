import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Head from 'next/head';
import { apiClient } from '../../utils/api';
import { getCurrentLocation } from '../../utils/geolocation';
import MapSelector from '../../components/MapSelector';

interface Course {
  id: number;
  name: string;
  code: string;
}

export default function CreateSession() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    course_id: '',
    start_time: '',
    end_time: '',
    location_radius: '100'
  });
  const [location, setLocation] = useState<{lat: number, lng: number, accuracy: number} | null>(null);
  const [manualLocation, setManualLocation] = useState<{lat: string, lng: string}>({lat: '', lng: ''});
  const [locationMethod, setLocationMethod] = useState<'auto' | 'manual'>('auto');
  const [locationError, setLocationError] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [step, setStep] = useState<'form' | 'location' | 'confirm'>('form');
  const router = useRouter();

  useEffect(() => {
    fetchCourses();
    getLocation();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await apiClient.get('/courses/lecturer');
      setCourses(response.data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError('Failed to load courses');
      }
    } finally {
      setLoading(false);
    }
  };

  const getLocation = async () => {
    try {
      setLocationError('');
      const locationData = await getCurrentLocation();
      setLocation({
        lat: locationData.latitude,
        lng: locationData.longitude,
        accuracy: locationData.accuracy
      });
      setLocationMethod('auto');
    } catch (error: any) {
      setLocationError(error.message || 'Failed to get location');
      setLocationMethod('manual');
    }
  };

  const handleManualLocationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setManualLocation({
      ...manualLocation,
      [e.target.name]: e.target.value
    });
  };

  const setManualLocationData = () => {
    const lat = parseFloat(manualLocation.lat);
    const lng = parseFloat(manualLocation.lng);
    
    if (isNaN(lat) || isNaN(lng)) {
      setLocationError('Please enter valid latitude and longitude');
      return;
    }
    
    if (lat < -90 || lat > 90) {
      setLocationError('Latitude must be between -90 and 90');
      return;
    }
    
    if (lng < -180 || lng > 180) {
      setLocationError('Longitude must be between -180 and 180');
      return;
    }
    
    setLocation({
      lat,
      lng,
      accuracy: 0
    });
    setLocationError('');
    setLocationMethod('manual');
  };

  const useFUTALocation = () => {
    // FUTA coordinates
    setLocation({
      lat: 7.3000,
      lng: 5.1450,
      accuracy: 0
    });
    setLocationError('');
    setLocationMethod('manual');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!location) {
      setError('Location is required to create a session');
      return;
    }

    if (!formData.course_id) {
      setError('Please select a course');
      return;
    }

    setCreating(true);
    setError('');

    try {
      await apiClient.post('/attendance/sessions', {
        title: formData.title,
        course_id: parseInt(formData.course_id),
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
        location_lat: location.lat,
        location_lng: location.lng,
        location_radius: parseFloat(formData.location_radius)
      });

      setSuccess('Session created successfully!');
      setTimeout(() => {
        router.push('/lecturer/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create session');
    } finally {
      setCreating(false);
    }
  };

  const selectedCourse = courses.find(c => c.id === parseInt(formData.course_id));

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading courses...</p>
        </div>
      </div>
    );
  }

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
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link
                href="/lecturer/dashboard"
                className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center hover:bg-gray-200 transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Create Attendance Session</h1>
                <p className="text-sm text-gray-500">Start a new attendance session for your students</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-red-700 font-medium">{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-red-500 hover:text-red-700"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center space-x-3">
              <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-green-700 font-medium">{success}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="px-8 py-6 border-b border-gray-100">
                <h2 className="text-2xl font-bold text-gray-900">Session Details</h2>
                <p className="text-gray-600 mt-1">Configure your attendance session</p>
              </div>

              <div className="p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
                      Session Title *
                    </label>
                    <input
                      id="title"
                      name="title"
                      type="text"
                      required
                      value={formData.title}
                      onChange={handleInputChange}
                      className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                      placeholder="e.g., Morning Lecture - Week 5"
                    />
                  </div>

                  <div>
                    <label htmlFor="course_id" className="block text-sm font-semibold text-gray-700 mb-2">
                      Select Course *
                    </label>
                    <select
                      id="course_id"
                      name="course_id"
                      required
                      value={formData.course_id}
                      onChange={handleInputChange}
                      className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    >
                      <option value="">Choose a course</option>
                      {courses.map((course) => (
                        <option key={course.id} value={course.id}>
                          {course.name} ({course.code})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="start_time" className="block text-sm font-semibold text-gray-700 mb-2">
                        Start Time *
                      </label>
                      <input
                        id="start_time"
                        name="start_time"
                        type="datetime-local"
                        required
                        value={formData.start_time}
                        onChange={handleInputChange}
                        className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                      />
                    </div>
                    <div>
                      <label htmlFor="end_time" className="block text-sm font-semibold text-gray-700 mb-2">
                        End Time *
                      </label>
                      <input
                        id="end_time"
                        name="end_time"
                        type="datetime-local"
                        required
                        value={formData.end_time}
                        onChange={handleInputChange}
                        className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="location_radius" className="block text-sm font-semibold text-gray-700 mb-2">
                      Location Radius (meters) *
                    </label>
                    <input
                      id="location_radius"
                      name="location_radius"
                      type="number"
                      min="10"
                      max="1000"
                      required
                      value={formData.location_radius}
                      onChange={handleInputChange}
                      className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      Students must be within this radius to mark attendance
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 pt-6">
                    <button
                      type="button"
                      onClick={() => router.push('/lecturer/dashboard')}
                      className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={creating || !location}
                      className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    >
                      {creating ? (
                        <div className="flex items-center justify-center space-x-2">
                          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span>Creating Session...</span>
                        </div>
                      ) : (
                        'Create Session'
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Location Setup with Map */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-bold text-gray-900">📍 Session Location</h3>
                <p className="text-sm text-gray-500">Select where the class will be held</p>
              </div>
              <div className="p-6">
                {location ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium text-green-600">Location Selected</span>
                    </div>
                    <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                      <p><span className="font-medium">Coordinates:</span> {location.lat.toFixed(6)}, {location.lng.toFixed(6)}</p>
                    </div>
                    <button
                      onClick={() => setLocation(null)}
                      className="w-full bg-blue-100 text-blue-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                    >
                      📍 Change Location
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <MapSelector
                      onLocationSelect={(lat, lng) => {
                        setLocation({ lat, lng, accuracy: 0 });
                        setLocationError('');
                      }}
                      height="300px"
                    />
                    
                    <div className="space-y-3">
                      <div className="flex space-x-2">
                        <button
                          onClick={getLocation}
                          className="flex-1 bg-blue-100 text-blue-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                        >
                          📱 Use My Location
                        </button>
                        <button
                          onClick={useFUTALocation}
                          className="flex-1 bg-green-100 text-green-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                        >
                          🏫 FUTA Campus
                        </button>
                      </div>
                      <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded-lg">
                        💡 <strong>Tip:</strong> Click on the map or drag the marker to select any location manually
                      </div>
                    </div>
                    
                    {locationError && (
                      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                        <div className="flex items-start space-x-3">
                          <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div className="flex-1">
                            <p className="text-sm font-medium text-red-800 mb-2">{locationError}</p>
                            {locationError.includes('denied') && (
                              <div className="text-xs text-red-700 space-y-1">
                                <p className="font-medium">To enable location access:</p>
                                <ul className="list-disc list-inside space-y-1 ml-2">
                                  <li>Click the location icon (🔒) in your browser's address bar</li>
                                  <li>Select "Allow" for location permissions</li>
                                  <li>Refresh the page and try again</li>
                                </ul>
                                <p className="mt-2 text-red-600">Or use the map below to manually select your location</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Session Preview */}
            {selectedCourse && (
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100">
                  <h3 className="text-lg font-bold text-gray-900">Session Preview</h3>
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Course</p>
                    <p className="text-lg font-bold text-gray-900">{selectedCourse.name}</p>
                    <p className="text-sm text-gray-600">{selectedCourse.code}</p>
                  </div>
                  {formData.title && (
                    <div>
                      <p className="text-sm font-medium text-gray-500">Title</p>
                      <p className="text-gray-900">{formData.title}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-500">Radius</p>
                    <p className="text-gray-900">{formData.location_radius}m</p>
                  </div>
                  {location && (
                    <div>
                      <p className="text-sm font-medium text-gray-500">Location</p>
                      <p className="text-xs text-gray-600">
                        {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tips */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
              <h3 className="text-lg font-bold text-blue-900 mb-3">💡 Tips</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Use descriptive session titles</li>
                <li>• Set appropriate location radius</li>
                <li>• Ensure stable internet connection</li>
                <li>• Students need face registration</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
      </div>
    </>
  );
}