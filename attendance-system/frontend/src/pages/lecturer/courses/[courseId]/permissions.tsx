import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { apiClient } from '../../../../utils/api';

interface Permission {
  id: number;
  lecturer_name: string;
  granted_at: string;
}

export default function CoursePermissions() {
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [newLecturerName, setNewLecturerName] = useState('');
  const [loading, setLoading] = useState(true);
  const [granting, setGranting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const router = useRouter();
  const { courseId } = router.query;

  useEffect(() => {
    if (courseId) {
      fetchPermissions();
    }
  }, [courseId]);

  const fetchPermissions = async () => {
    try {
      const response = await apiClient.get(`/courses/${courseId}/permissions`);
      setPermissions(response.data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError('Failed to load permissions');
      }
    } finally {
      setLoading(false);
    }
  };

  const grantPermission = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLecturerName.trim()) return;

    setGranting(true);
    setError('');
    setSuccess('');

    try {
      await apiClient.post(`/courses/${courseId}/permissions`, {
        lecturer_name: newLecturerName.trim()
      });
      
      setSuccess(`Permission granted to ${newLecturerName}`);
      setNewLecturerName('');
      fetchPermissions();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to grant permission');
    } finally {
      setGranting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading permissions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link
                href="/lecturer/courses"
                className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center hover:bg-gray-200 transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Course Permissions</h1>
                <p className="text-sm text-gray-500">Manage lecturer access to Course ID: {courseId}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl">
            <p className="text-green-700 font-medium">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Grant Permission Form */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-8 py-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Grant Access</h2>
              <p className="text-gray-600 mt-1">Allow another lecturer to view this course</p>
            </div>

            <div className="p-8">
              <form onSubmit={grantPermission} className="space-y-6">
                <div>
                  <label htmlFor="lecturer_name" className="block text-sm font-semibold text-gray-700 mb-2">
                    Lecturer Name *
                  </label>
                  <input
                    id="lecturer_name"
                    type="text"
                    required
                    value={newLecturerName}
                    onChange={(e) => setNewLecturerName(e.target.value)}
                    className="block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Enter lecturer's full name"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Enter the exact name as registered in the system
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={granting || !newLecturerName.trim()}
                  className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-green-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {granting ? (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Granting Access...</span>
                    </div>
                  ) : (
                    '🔑 Grant Access'
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Current Permissions */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-8 py-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Current Access ({permissions.length})</h2>
              <p className="text-gray-600 mt-1">Lecturers with access to this course</p>
            </div>

            <div className="p-8">
              {permissions.length > 0 ? (
                <div className="space-y-4">
                  {permissions.map((permission) => (
                    <div key={permission.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                      <div>
                        <h3 className="font-semibold text-gray-900">{permission.lecturer_name}</h3>
                        <p className="text-sm text-gray-500">
                          Granted: {new Date(permission.granted_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          ✓ Active
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2">No Additional Access</h3>
                  <p className="text-gray-600">Only you have access to this course currently.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-2xl p-6">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">About Course Permissions</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Granted lecturers can view course students and attendance reports</li>
                <li>• They cannot create sessions or modify course settings</li>
                <li>• Only course owners can grant or revoke permissions</li>
                <li>• Permissions are permanent until manually revoked</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}