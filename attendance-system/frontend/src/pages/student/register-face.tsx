import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/router';
import Webcam from 'react-webcam';
import { apiClient } from '../../utils/api';

export default function RegisterFace() {
  const [step, setStep] = useState<'instructions' | 'capture' | 'testing' | 'processing' | 'success'>('instructions');
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [qualityResult, setQualityResult] = useState<any>(null);
  const [registrationResult, setRegistrationResult] = useState<any>(null);
  const webcamRef = useRef<Webcam>(null);
  const router = useRouter();

  const capture = useCallback(async () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setStep('testing');
      
      // Test face quality first
      try {
        const response = await apiClient.post('/auth/test-face-quality', {
          face_image_data: imageSrc
        });
        setQualityResult(response.data);
        setStep('processing');
      } catch (err: any) {
        setError(err.response?.data?.message || 'Face quality test failed');
        setQualityResult(err.response?.data || null);
        setStep('processing');
      }
    }
  }, [webcamRef]);

  const retake = () => {
    setCapturedImage(null);
    setQualityResult(null);
    setRegistrationResult(null);
    setStep('capture');
    setError('');
  };

  const registerFace = async () => {
    if (!capturedImage) return;

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/auth/register-face', {
        face_image_data: capturedImage
      });
      
      setRegistrationResult(response.data);
      setStep('success');
      
      setTimeout(() => {
        router.push('/student/dashboard');
      }, 5000);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Face registration failed. Please try again.');
      setStep('processing');
    } finally {
      setLoading(false);
    }
  };

  const skipForNow = () => {
    router.push('/student/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Face Registration</h1>
          <p className="text-gray-600">Set up secure biometric authentication</p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
          {error && (
            <div className="p-6 bg-red-50 border-b border-red-100">
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-red-700 font-medium">{error}</p>
              </div>
            </div>
          )}

          {step === 'instructions' && (
            <div className="p-8">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Before We Start</h2>
                <p className="text-gray-600">Follow these guidelines for the best results</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center p-6 bg-blue-50 rounded-xl">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Good Lighting</h3>
                  <p className="text-sm text-gray-600">Ensure you're in a well-lit area</p>
                </div>

                <div className="text-center p-6 bg-green-50 rounded-xl">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Look Directly</h3>
                  <p className="text-sm text-gray-600">Face the camera straight on</p>
                </div>

                <div className="text-center p-6 bg-purple-50 rounded-xl">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Clear View</h3>
                  <p className="text-sm text-gray-600">Remove glasses, hats, or masks</p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={() => setStep('capture')}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-[1.02]"
                >
                  Start Face Registration
                </button>
                <button
                  onClick={skipForNow}
                  className="flex-1 bg-gray-100 text-gray-700 py-4 px-6 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                >
                  Skip for Now
                </button>
              </div>
            </div>
          )}

          {step === 'capture' && (
            <div className="p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Position Your Face</h2>
                <p className="text-gray-600">Center your face in the frame below</p>
              </div>

              <div className="relative mb-8">
                <div className="relative inline-block mx-auto">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    className="rounded-2xl shadow-lg w-full max-w-md mx-auto"
                    width={400}
                    height={300}
                  />
                  <div className="absolute inset-0 border-4 border-blue-500 rounded-2xl pointer-events-none">
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-2 border-blue-300 rounded-full opacity-50"></div>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={capture}
                  className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 text-white py-4 px-6 rounded-xl font-semibold hover:from-green-700 hover:to-blue-700 transition-all duration-200"
                >
                  Capture Photo
                </button>
                <button
                  onClick={() => setStep('instructions')}
                  className="flex-1 bg-gray-100 text-gray-700 py-4 px-6 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                >
                  Back
                </button>
              </div>
            </div>
          )}

          {step === 'testing' && (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto mb-6"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Face Quality</h2>
              <p className="text-gray-600">Please wait while we check your photo...</p>
            </div>
          )}

          {step === 'processing' && capturedImage && (
            <div className="p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Review Your Photo</h2>
                <p className="text-gray-600">Quality analysis complete</p>
              </div>

              <div className="mb-6 text-center">
                <img
                  src={capturedImage}
                  alt="Captured face"
                  className="mx-auto rounded-2xl shadow-lg max-w-sm border-4 border-gray-200"
                />
              </div>

              {/* Quality Results */}
              {qualityResult && (
                <div className={`mb-6 p-4 rounded-xl ${
                  qualityResult.success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-yellow-50 border border-yellow-200'
                }`}>
                  <div className="flex items-center space-x-3 mb-3">
                    {qualityResult.success ? (
                      <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                    <h3 className={`font-semibold ${
                      qualityResult.success ? 'text-green-800' : 'text-yellow-800'
                    }`}>
                      {qualityResult.success ? '✅ Good Quality' : '⚠️ Quality Issues'}
                    </h3>
                  </div>
                  
                  {qualityResult.quality_metrics && (
                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${
                          qualityResult.success ? 'text-green-600' : 'text-yellow-600'
                        }`}>
                          {Math.round(qualityResult.quality_metrics.quality_score * 100)}%
                        </div>
                        <div className="text-sm text-gray-600">Quality Score</div>
                      </div>
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${
                          qualityResult.success ? 'text-green-600' : 'text-yellow-600'
                        }`}>
                          {qualityResult.quality_metrics.status}
                        </div>
                        <div className="text-sm text-gray-600">Status</div>
                      </div>
                    </div>
                  )}
                  
                  {qualityResult.suggestions && (
                    <div className="text-sm text-yellow-700">
                      <p className="font-medium mb-2">💡 Suggestions:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {qualityResult.suggestions.map((suggestion: string, index: number) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={registerFace}
                  disabled={loading || (qualityResult && !qualityResult.success)}
                  className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-200 ${
                    loading || (qualityResult && !qualityResult.success)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:from-green-700 hover:to-emerald-700'
                  }`}
                >
                  {loading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Registering...</span>
                    </div>
                  ) : qualityResult && !qualityResult.success ? (
                    'Quality Too Low - Retake Photo'
                  ) : (
                    'Register This Photo'
                  )}
                </button>
                <button
                  onClick={retake}
                  disabled={loading}
                  className="flex-1 bg-gray-100 text-gray-700 py-4 px-6 rounded-xl font-semibold hover:bg-gray-200 disabled:opacity-50 transition-colors"
                >
                  Retake Photo
                </button>
              </div>
            </div>
          )}

          {step === 'success' && (
            <div className="p-8 text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Registration Successful! 🎉</h2>
              
              {registrationResult && (
                <div className="mb-6">
                  <p className="text-gray-600 mb-4">{registrationResult.message}</p>
                  
                  {registrationResult.quality_metrics && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
                      <h3 className="font-semibold text-green-800 mb-3">📊 Registration Quality</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {Math.round(registrationResult.quality_metrics.quality_score * 100)}%
                          </div>
                          <div className="text-sm text-gray-600">Quality Score</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {registrationResult.quality_metrics.status}
                          </div>
                          <div className="text-sm text-gray-600">Status</div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {registrationResult.tips && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                      <h3 className="font-semibold text-blue-800 mb-2">💡 Tips for Attendance</h3>
                      <ul className="text-sm text-blue-700 space-y-1">
                        {registrationResult.tips.map((tip: string, index: number) => (
                          <li key={index}>• {tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              <div className="bg-blue-50 rounded-xl p-4">
                <p className="text-sm text-blue-700">Redirecting to dashboard in 5 seconds...</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-500">
            🔒 Your face data is encrypted and stored securely for attendance verification only.<br/>
            ✨ High-quality face registration ensures accurate attendance marking.
          </p>
        </div>
      </div>
    </div>
  );
}