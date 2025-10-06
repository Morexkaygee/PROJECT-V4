# Vercel Deployment Guide

## Overview
This guide will help you deploy your Attendance Management System to Vercel. Due to the heavy ML dependencies (face recognition, TensorFlow), we'll deploy the frontend to Vercel and the backend separately.

## Frontend Deployment to Vercel

### Step 1: Prepare Your Repository
✅ Your repository is already prepared with the necessary configuration files.

### Step 2: Deploy to Vercel

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Click "New Project"**
3. **Import your GitHub repository**: `https://github.com/Morexkaygee/PROJECT-V4`
4. **Configure the project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `attendance-system/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

### Step 3: Environment Variables
In Vercel dashboard, add these environment variables:
- `NEXT_PUBLIC_API_URL`: Your backend API URL (see backend deployment options below)

### Step 4: Deploy
Click "Deploy" and wait for the build to complete.

## Backend Deployment Options

Since Vercel has limitations with heavy ML libraries, consider these alternatives for your FastAPI backend:

### Option 1: Railway (Recommended)
1. Go to [Railway](https://railway.app)
2. Connect your GitHub repository
3. Select the backend folder
4. Add environment variables (DATABASE_URL, SECRET_KEY, etc.)
5. Deploy

### Option 2: Render
1. Go to [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 3: DigitalOcean App Platform
1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Create a new app from GitHub
3. Configure Python service
4. Add environment variables

## Database Setup

### Option 1: Neon (PostgreSQL)
1. Go to [Neon](https://neon.tech)
2. Create a new database
3. Copy the connection string
4. Add as `DATABASE_URL` environment variable

### Option 2: Supabase
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Get the database URL from settings
4. Add as `DATABASE_URL` environment variable

## Environment Variables Needed

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (Railway/Render/etc.)
```
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Post-Deployment Steps

1. **Update CORS settings** in your backend to include your Vercel domain
2. **Run database migrations** on your deployed backend
3. **Test the connection** between frontend and backend
4. **Update API URLs** in your frontend if needed

## Troubleshooting

### Common Issues:
1. **CORS errors**: Update backend CORS settings
2. **API connection fails**: Check environment variables
3. **Build fails**: Check dependencies and build commands

### Logs:
- **Vercel**: Check function logs in Vercel dashboard
- **Backend**: Check logs in your backend hosting platform

## Alternative: Full-Stack Deployment

If you prefer to keep everything together, consider:
- **Heroku**: Supports both frontend and backend
- **DigitalOcean Droplet**: Full control over the environment
- **AWS EC2**: More complex but highly scalable

## Next Steps

1. Deploy frontend to Vercel
2. Deploy backend to Railway/Render
3. Set up database on Neon/Supabase
4. Configure environment variables
5. Test the full application