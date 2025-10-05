import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { apiClient } from '../../utils/api';

interface Session {
  id: number;
  title: string;
  course_name: string;
  course_code: string;
  created_at: string;
  is_active: boolean;
  attendance_count: number;
}

interface AttendanceRecord {
  id: number;
  student_name: string;
  student_matric: string;
  marked_at: string;
}

export default function LecturerReports() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingRecords, setLoadingRecords] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'closed'>('all');
  const router = useRouter();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await apiClient.get('/attendance/sessions/lecturer');
      setSessions(response.data);
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
    setLoadingRecords(true);
    try {
      const response = await apiClient.get(`/attendance/sessions/${sessionId}/attendance`);
      setAttendanceRecords(response.data);
    } catch (err: any) {
      setError('Failed to load attendance records');
    } finally {
      setLoadingRecords(false);
    }
  };

  const handleSessionSelect = (session: Session) => {
    setSelectedSession(session);
    fetchAttendanceRecords(session.id);
  };

  const exportAttendance = () => {
    if (!selectedSession || !attendanceRecords.length) return;

    const csvContent = [
      ['Student Name', 'Matric Number', 'Date & Time'].join(','),
      ...attendanceRecords.map(record => [
        record.student_name,
        record.student_matric,
        new Date(record.marked_at).toLocaleString()
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${selectedSession.title}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getFilteredSessions = () => {
    switch (filter) {
      case 'active':
        return sessions.filter(s => s.is_active);
      case 'closed':
        return sessions.filter(s => !s.is_active);
      default:
        return sessions;
    }
  };

  const filteredSessions = getFilteredSessions();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-100">
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
                <h1 className="text-xl font-bold text-gray-900">Attendance Reports</h1>
                <p className="text-sm text-gray-500">View and export attendance data</p>
              </div>
            </div>
            {selectedSession && attendanceRecords.length > 0 && (
              <button
                onClick={exportAttendance}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-200 transform hover:scale-105"
              >
                <svg className="w-5 h-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export CSV
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sessions Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="text-lg font-bold text-gray-900">My Sessions ({sessions.length})</h2>
                <p className="text-sm text-gray-600">Select a session to view reports</p>
              </div>
              
              {/* Filter Buttons */}
              <div className="px-6 py-4 border-b border-gray-100">
                <div className="flex space-x-2">
                  <button
                    onClick={() => setFilter('all')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      filter === 'all'
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => setFilter('active')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      filter === 'active'
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Active
                  </button>
                  <button
                    onClick={() => setFilter('closed')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      filter === 'closed'
                        ? 'bg-orange-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Closed
                  </button>
                </div>
              </div>

              <div className="p-6">
                {filteredSessions.length > 0 ? (
                  <div className="space-y-3">
                    {filteredSessions.map((session) => (
                      <div
                        key={session.id}
                        onClick={() => handleSessionSelect(session)}
                        className={`group p-4 border rounded-xl cursor-pointer transition-all duration-200 ${
                          selectedSession?.id === session.id
                            ? 'border-orange-500 bg-orange-50 shadow-md'
                            : 'border-gray-200 hover:border-orange-300 hover:shadow-sm'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold text-gray-900 group-hover:text-orange-600 transition-colors">
                            {session.title}
                          </h3>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            session.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            <div className={`w-2 h-2 rounded-full mr-1 ${
                              session.is_active ? 'bg-green-400' : 'bg-gray-400'
                            }`}></div>
                            {session.is_active ? 'Active' : 'Closed'}
                          </span>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-2">{session.course_name}</p>
                        <p className="text-xs text-gray-500 mb-2">{session.course_code}</p>
                        
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{new Date(session.created_at).toLocaleDateString()}</span>
                          <span className="font-medium text-orange-600">
                            {session.attendance_count} attended
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <p className="text-sm text-gray-500">
                      {filter === 'all' ? 'No sessions created yet' : `No ${filter} sessions`}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
              {selectedSession ? (
                <>
                  <div className="px-8 py-6 border-b border-gray-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedSession.title}</h2>
                        <p className="text-gray-600">{selectedSession.course_name} ({selectedSession.course_code})</p>
                        <p className="text-sm text-gray-500 mt-1">
                          Created: {new Date(selectedSession.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-orange-600">{selectedSession.attendance_count}</div>
                        <div className="text-sm text-gray-500">Students Present</div>
                      </div>
                    </div>
                  </div>

                  <div className="p-8">
                    {loadingRecords ? (
                      <div className="flex justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-600 border-t-transparent"></div>
                      </div>
                    ) : attendanceRecords.length > 0 ? (
                      <div className="space-y-4">
                        {attendanceRecords.map((record) => (
                          <div key={record.id} className="group bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-6 border border-orange-200 hover:shadow-lg transition-all duration-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                                  <span className="text-white font-bold text-lg">
                                    {record.student_name.charAt(0).toUpperCase()}
                                  </span>
                                </div>
                                
                                <div>
                                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-orange-600 transition-colors">
                                    {record.student_name}
                                  </h3>
                                  <p className="text-sm text-gray-600">{record.student_matric}</p>
                                </div>
                              </div>
                              
                              <div className="text-right">
                                <div className="text-sm text-gray-500">Marked at</div>
                                <div className="text-lg font-bold text-gray-900">
                                  {new Date(record.marked_at).toLocaleTimeString([], { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                  })}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {new Date(record.marked_at).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-16">
                        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                          <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                          </svg>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">No attendance records</h3>
                        <p className="text-gray-600">No students have marked attendance for this session yet.</p>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="p-16 text-center">
                  <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Select a session</h3>
                  <p className="text-gray-600 mb-6">Choose a session from the sidebar to view detailed attendance reports.</p>
                  <Link
                    href="/lecturer/create-session"
                    className="inline-flex items-center bg-orange-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-orange-700 transition-colors"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Create New Session
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}