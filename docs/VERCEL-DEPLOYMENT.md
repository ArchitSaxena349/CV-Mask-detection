# 🚀 Vercel Deployment Guide

This guide explains how to deploy the Mask Detection System to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Vercel CLI** (optional): `npm install -g vercel`

## 🎯 Quick Deployment

### Method 1: Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure settings**:
   - Framework Preset: `Other`
   - Root Directory: `./` (leave empty)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. **Add Environment Variables**:
   - `FLASK_CONFIG` = `production`
   - `SECRET_KEY` = `your-secret-key-here`
6. **Click "Deploy"**

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name? mask-detection-system
# - Directory? ./
```

## 🔧 Configuration Files

The following files are configured for Vercel deployment:

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### `api/index.py`
- Vercel entry point
- Imports the main Flask application
- Configured for serverless deployment

### `app.py`
- Simplified Flask application
- Basic face detection (no ML model)
- Web interface for image upload

## 🌐 Accessing Your Deployed App

After deployment, Vercel will provide you with:
- **Production URL**: `https://your-project-name.vercel.app`
- **Preview URLs**: For each deployment

### Available Endpoints:
- **Home**: `https://your-app.vercel.app/`
- **Face Detection API**: `https://your-app.vercel.app/api/detect`
- **Health Check**: `https://your-app.vercel.app/api/health`

## ⚠️ Limitations on Vercel

Due to Vercel's serverless nature, some features are limited:

### ❌ Not Available:
- **Real-time camera feed** (requires persistent connections)
- **Large ML models** (file size and memory limits)
- **TensorFlow/Keras** (too large for serverless)
- **Video processing** (execution time limits)

### ✅ Available:
- **Basic face detection** using OpenCV
- **Image upload and processing**
- **Web interface**
- **API endpoints**
- **Health monitoring**

## 🔧 Environment Variables

Set these in your Vercel dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_CONFIG` | `production` | Flask configuration |
| `SECRET_KEY` | `your-secret-key` | Flask secret key |

## 📊 Performance Considerations

### Vercel Limits:
- **Function Duration**: 30 seconds max
- **Memory**: 1024 MB max
- **File Size**: 50 MB max per file
- **Deployment Size**: 100 MB max

### Optimizations:
- ✅ Removed large ML models
- ✅ Used lightweight OpenCV
- ✅ Simplified dependencies
- ✅ Optimized image processing

## 🐛 Troubleshooting

### Common Issues:

#### 1. Build Fails
```
Error: No flask entrypoint found
```
**Solution**: Ensure `app.py` or `api/index.py` exists

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'tensorflow'
```
**Solution**: TensorFlow is not supported on Vercel, use the simplified version

#### 3. Function Timeout
```
Function execution timed out
```
**Solution**: Optimize image processing or reduce image size

#### 4. Memory Limit Exceeded
```
Function exceeded memory limit
```
**Solution**: Process smaller images or optimize code

## 🔄 Continuous Deployment

Vercel automatically deploys when you:
1. **Push to main branch** (production deployment)
2. **Create pull request** (preview deployment)
3. **Push to any branch** (preview deployment)

## 📈 Monitoring

### Vercel Dashboard:
- **Function logs**: View execution logs
- **Analytics**: Monitor performance
- **Deployments**: Track deployment history

### Custom Monitoring:
- **Health endpoint**: `/api/health`
- **Error tracking**: Built into Flask app
- **Performance metrics**: Available in Vercel dashboard

## 🚀 Next Steps

After successful deployment:

1. **Test the application**: Upload images and verify face detection
2. **Monitor performance**: Check Vercel analytics
3. **Set up custom domain** (optional): Configure in Vercel dashboard
4. **Add more features**: Extend the API as needed

## 📞 Support

If you encounter issues:
1. Check Vercel function logs
2. Review this deployment guide
3. Check Vercel documentation: https://vercel.com/docs
4. Create an issue on GitHub

---

**Your Mask Detection System is now live on Vercel!** 🎉