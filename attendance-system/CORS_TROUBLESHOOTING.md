# CORS Troubleshooting Guide

## Overview
This guide helps resolve Cross-Origin Resource Sharing (CORS) issues in the Attendance Management System.

## Common CORS Issues Fixed

### 1. Wildcard Origins Removed
**Issue**: Backend was using `allow_origins=["*"]` which is insecure and can cause issues with credentials.

**Fix**: 
- Replaced with specific allowed origins
- Added environment-based configuration
- Supports development, staging, and production environments

### 2. Frontend API Configuration
**Issue**: Frontend was hardcoded to localhost only.

**Fix**:
- Updated to use environment variables
- Added proper CORS headers
- Enabled credentials support

### 3. Environment-Based CORS
**Issue**: No distinction between development and production CORS settings.

**Fix**:
- Created `app/core/cors.py` for centralized CORS management
- Added environment-specific configurations
- Support for dynamic origin detection

## Configuration Files Updated

### Backend Files:
1. `app/main.py` - Updated CORS middleware configuration
2. `app/core/config.py` - Added CORS origins to settings
3. `app/core/cors.py` - New centralized CORS configuration
4. `simple_server.py` - Fixed wildcard CORS issue
5. `.env` - Added CORS_ORIGINS environment variable
6. `.env.example` - Added CORS configuration examples
7. `.env.production` - Production-ready CORS settings

### Frontend Files:
1. `src/utils/api.ts` - Updated API client with proper CORS headers
2. `.env.local` - Set proper default API URL

## Environment Variables

### Development (.env)
```bash
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
ENVIRONMENT=development
```

### Staging
```bash
CORS_ORIGINS=["https://staging-attendance.futa.edu.ng", "http://localhost:3000"]
ENVIRONMENT=staging
STAGING_CORS_ORIGINS=["https://staging-attendance.futa.edu.ng"]
```

### Production
```bash
CORS_ORIGINS=["https://attendance.futa.edu.ng", "https://www.attendance.futa.edu.ng"]
ENVIRONMENT=production
PRODUCTION_CORS_ORIGINS=["https://attendance.futa.edu.ng", "https://www.attendance.futa.edu.ng"]
```

## Testing CORS Configuration

### 1. Check Current CORS Settings
```bash
# Start the backend server
cd backend
python -m uvicorn app.main:app --reload

# Check CORS origins in console output
# Should show: "CORS Origins: ['http://localhost:3000', ...]"
```

### 2. Test Frontend Connection
```bash
# Start frontend server
cd frontend
npm run dev

# Open browser console and check for CORS errors
# Should not see "Access-Control-Allow-Origin" errors
```

### 3. Test API Endpoints
```bash
# Test with curl
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type,Authorization" \
     -X OPTIONS \
     http://localhost:8000/auth/login

# Should return 200 OK with proper CORS headers
```

## Common CORS Error Messages and Solutions

### Error: "Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:3000' has been blocked by CORS policy"

**Solution**: 
1. Check that `http://localhost:3000` is in your CORS_ORIGINS
2. Restart the backend server after changing .env
3. Clear browser cache

### Error: "CORS policy: The request client is not a secure context"

**Solution**:
1. Use HTTPS in production
2. For development, ensure localhost is used (not IP addresses)
3. Check SSL certificate configuration

### Error: "CORS policy: Credentials mode is 'include'"

**Solution**:
1. Ensure `allow_credentials=True` in CORS configuration
2. Don't use wildcard origins with credentials
3. Check that frontend sets `withCredentials: true`

## Mobile/Ngrok CORS Issues

### For Ngrok URLs:
1. Add your ngrok URL to CORS_ORIGINS:
```bash
CORS_ORIGINS=["http://localhost:3000", "https://your-ngrok-url.ngrok.io"]
```

2. Update frontend .env.local:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-ngrok-url.ngrok.io
```

### For Mobile Testing:
1. Use your computer's IP address:
```bash
CORS_ORIGINS=["http://localhost:3000", "http://192.168.1.100:3000"]
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

## Security Best Practices

1. **Never use wildcard origins** (`*`) in production
2. **Always specify exact origins** including protocol and port
3. **Use HTTPS in production** for secure contexts
4. **Limit allowed methods** to only what's needed
5. **Specify allowed headers** explicitly
6. **Set appropriate max-age** for preflight caching
7. **Enable credentials only when necessary**

## Debugging CORS Issues

### 1. Browser Developer Tools
- Open Network tab
- Look for OPTIONS requests (preflight)
- Check response headers for CORS headers
- Look for error messages in Console tab

### 2. Backend Logs
- Check server console for CORS configuration output
- Look for origin validation messages
- Check for middleware errors

### 3. Test with Different Browsers
- Chrome has strict CORS enforcement
- Firefox may show different error messages
- Safari has unique CORS behaviors

## Production Deployment Checklist

- [ ] Update CORS_ORIGINS with production domains
- [ ] Set ENVIRONMENT=production
- [ ] Remove development origins from production
- [ ] Enable HTTPS/SSL
- [ ] Test all API endpoints from frontend
- [ ] Verify mobile browser compatibility
- [ ] Check preflight request handling
- [ ] Validate credential handling

## Contact Information

For additional CORS issues or questions:
- Check the FastAPI CORS documentation
- Review browser-specific CORS implementations
- Test with different network configurations
- Consider using a CORS testing tool