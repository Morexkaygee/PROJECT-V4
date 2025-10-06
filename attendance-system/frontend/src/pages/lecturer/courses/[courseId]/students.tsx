import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { apiClient } from '../../../../utils/api';

interface Student {
  id: number;
  name: string;
  matric_no: string;
  has_facial_encoding: boolean;
  attendance_count: number;
  department?: string;
  level?: string;
  face_registered?: boolean;
}

export default function CourseStudents() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();
  const { courseId } = router.query;

  useEffect(() => {
    if (courseId) {
      fetchCourseStudents();
    }
  }, [courseId]);

  const fetchCourseStudents = async () => {
    try {
      console.log('Fetching students for course:', courseId);
      const response = await apiClient.get(`/courses/${courseId}/students`);
      console.log('Course students response:', response.data);
      setStudents(response.data);
      setError(''); // Clear any previous errors
    } catch (err: any) {
      console.error('Course students API error:', err);
      if (err.response?.status === 401) {
        router.push('/login');
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to server. Please check if the backend is running.');
      } else {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to load course students';
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading students...</p>
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
                <h1 className="text-xl font-bold text-gray-900">Course Students</h1>
                <p className="text-sm text-gray-500">Course ID: {courseId}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className={`mb-6 p-4 rounded-xl ${
            error.includes('temporarily unavailable') 
              ? 'bg-blue-50 border border-blue-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center justify-between">
              <p className={`font-medium ${
                error.includes('temporarily unavailable') 
                  ? 'text-blue-700' 
                  : 'text-red-700'
              }`}>{error}</p>
              {!error.includes('temporarily unavailable') && (
                <button
                  onClick={fetchCourseStudents}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
                >
                  Retry
                </button>
              )}
            </div>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="px-8 py-6 border-b border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900">Enrolled Students ({students.length})</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Student</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Matric Number</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Face Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Attendance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {students.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-sm">
                            {student.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <span className="font-medium text-gray-900">{student.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{student.matric_no}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        student.has_facial_encoding 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {student.has_facial_encoding ? '✓ Registered' : '✗ Not Registered'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">{student.attendance_count} sessions</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {students.length === 0 && (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">No Students Enrolled</h3>
              <p className="text-gray-600">No students have enrolled in this course yet.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}