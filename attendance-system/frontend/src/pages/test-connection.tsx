import { useState } from 'react';
import { apiClient } from '../utils/api';

export default function TestConnection() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testConnection = async () => {
    setLoading(true);
    setResult('Testing connection...');
    
    try {
      // Test basic connection
      const response = await apiClient.get('/health');
      setResult(`✅ Backend connected! Response: ${JSON.stringify(response.data)}`);
    } catch (error: any) {
      setResult(`❌ Connection failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    setResult('Testing login...');
    
    try {
      const response = await apiClient.post('/auth/login/student', {
        matric_no: 'IFT/19/0644',
        password: 'newpass123'
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        setResult(`✅ Login successful! User: ${response.data.user.name}`);
      }
    } catch (error: any) {
      setResult(`❌ Login failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold mb-6">Connection Test</h1>
        
        <div className="space-y-4">
          <button
            onClick={testConnection}
            disabled={loading}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            Test Backend Connection
          </button>
          
          <button
            onClick={testLogin}
            disabled={loading}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50 ml-4"
          >
            Test Login
          </button>
        </div>
        
        <div className="mt-6 p-4 bg-gray-50 rounded">
          <h3 className="font-semibold mb-2">Result:</h3>
          <pre className="whitespace-pre-wrap">{result}</pre>
        </div>
        
        <div className="mt-4">
          <a href="/student/dashboard" className="text-blue-500 hover:underline">
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}