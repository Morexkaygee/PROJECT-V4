import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { apiClient } from '../../../../utils/api';

interface AttendanceRecord {
  student_name: string;
  matric_no: string;
  marked_at: string;
  present: boolean;
  verification_method: string;
}

interface Session {
  id: number;
  title: string;
  created_at: string;
  attendance_count: number;
  course_id: number;
}

export default function CourseReports() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();
  const { courseId } = router.query;

  useEffect(() => {
    if (courseId) {
      fetchSessions();
    }
  }, [courseId]);

  const fetchSessions = async () => {
    try {
      const response = await apiClient.get('/attendance/sessions/lecturer');
      const courseSessions = response.data.filter((session: Session) => session.course_id === parseInt(courseId as string));
      setSessions(courseSessions);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError('Failed to load sessions');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendanceRecords = async (sessionId: number) => {
    try {
      const response = await apiClient.get(`/attendance/sessions/${sessionId}/attendance`);
      setAttendanceRecords(response.data);
      setSelectedSession(sessionId);
    } catch (err: any) {
      setError('Failed to load attendance records');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-green-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading reports...</p>
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
                <h1 className="text-xl font-bold text-gray-900">Course Reports</h1>
                <p className="text-sm text-gray-500">Course ID: {courseId}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sessions List */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-8 py-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Attendance Sessions</h2>
            </div>
            
            <div className="p-6 space-y-4">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => fetchAttendanceRecords(session.id)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    selectedSession === session.id
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-green-300 hover:bg-gray-50'
                  }`}
                >
                  <h3 className="font-bold text-gray-900">{session.title}</h3>
                  <p className="text-sm text-gray-600">{new Date(session.created_at).toLocaleDateString()}</p>
                  <p className="text-sm text-green-600">{session.attendance_count} attendees</p>
                </div>
              ))}
              
              {sessions.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-500">No sessions found for this course</p>
                </div>
              )}
            </div>
          </div>

          {/* Attendance Records */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="px-8 py-6 border-b border-gray-100">
              <h2 className="text-2xl font-bold text-gray-900">Attendance Records</h2>
            </div>
            
            {selectedSession ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Student</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Time</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Method</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {attendanceRecords.map((record, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{record.student_name}</div>
                            <div className="text-sm text-gray-500">{record.matric_no}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(record.marked_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            {record.verification_method}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                
                {attendanceRecords.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No attendance records for this session</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Select a Session</h3>
                <p className="text-gray-600">Choose a session from the left to view attendance records</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}