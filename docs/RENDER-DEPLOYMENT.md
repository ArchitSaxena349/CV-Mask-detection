# 🚀 Render Deployment Guide - Full Features!

Deploy the complete Mask Detection System to Render with **ALL features enabled**!

## 🎯 Why Render?

Unlike serverless platforms, Render provides:
- ✅ **Full TensorFlow/Keras support**
- ✅ **Real-time camera feeds**
- ✅ **Complete ML model loading**
- ✅ **Persistent containers**
- ✅ **WebSocket support**
- ✅ **No execution time limits**
- ✅ **Free tier available**

## 🚀 Quick Deployment

### Method 1: Render Dashboard (Recommended)

1. **Sign up at [render.com](https://render.com)**
2. **Connect your GitHub account**
3. **Click "New +" → "Web Service"**
4. **Select your repository**
5. **Configure settings**:
   ```
   Name: mask-detection-system
   Environment: Python 3
   Build Command: pip install -r requirements-render.txt
   Start Command: python serve.py
   ```
6. **Add Environment Variables**:
   ```
   FLASK_CONFIG = production
   HOST = 0.0.0.0
   PORT = 10000
   SECRET_KEY = your-secret-key-here
   ```
7. **Click "Create Web Service"**

### Method 2: render.yaml (Infrastructure as Code)

1. **Commit the `render.yaml` file** to your repository
2. **Go to Render Dashboard**
3. **Click "New +" → "Blueprint"**
4. **Select your repository**
5. **Render will automatically configure everything!**

## 🔧 Configuration Files

### `render.yaml` (Complete Setup)
```yaml
services:
  - type: web
    name: mask-detection-system
    env: python
    plan: starter
    buildCommand: pip install -r requirements-render.txt
    startCommand: python serve.py
    envVars:
      - key: FLASK_CONFIG
        value: production
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /api/v1/health
```

### `requirements-render.txt` (Full Features)
```txt
Flask==3.1.1
tensorflow-cpu>=2.16.0,<2.21.0
opencv-contrib-python-headless==4.10.0.84
numpy>=1.24.0,<2.0.0
# ... all dependencies included with version ranges for compatibility
```

## 🌟 Full Features Available

### ✅ **Complete Functionality**:
- **🎥 Real-time camera detection**
- **🤖 Full ML model with mask classification**
- **📷 Image upload and processing**
- **🔴 Red boxes for "No Mask"**
- **🟢 Green boxes for "Mask Detected"**
- **📊 Confidence percentages**
- **📈 Health monitoring**
- **📱 Responsive web interface**

### 🎮 **Available Endpoints**:
- **Home**: `https://your-app.onrender.com/`
- **Image Detector**: `https://your-app.onrender.com/image-mask-detector`
- **Video Feed**: `https://your-app.onrender.com/video_feed`
- **Health Check**: `https://your-app.onrender.com/api/v1/health`
- **Metrics**: `https://your-app.onrender.com/api/v1/metrics`

## 💰 Pricing Plans

### Free Tier (Starter Plan):
- ✅ **512 MB RAM**
- ✅ **0.1 CPU**
- ✅ **Sleeps after 15 min inactivity**
- ✅ **Perfect for demos and testing**

### Paid Plans (Starting $7/month):
- ✅ **Always-on service**
- ✅ **More RAM and CPU**
- ✅ **Custom domains**
- ✅ **Better performance**

## 🔧 Environment Variables

Set these in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_CONFIG` | `production` | Flask environment |
| `SECRET_KEY` | `auto-generated` | Flask secret key |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `10000` | Server port (Render default) |
| `THREADS` | `4` | Number of threads |

## 📊 Performance Optimization

### Build Optimization:
```bash
# In render.yaml
buildCommand: |
  pip install --upgrade pip
  pip install --no-cache-dir -r requirements-render.txt
```

### Runtime Optimization:
- **Multi-threading**: 4 threads for concurrent requests
- **Connection pooling**: 1000 connection limit
- **Memory management**: Optimized for 512MB RAM
- **Model caching**: TensorFlow model loaded once

## 🐛 Troubleshooting

### Common Issues:

#### 1. Build Timeout
```
Build exceeded time limit
```
**Solution**: Use `requirements-render.txt` (optimized dependencies)

#### 2. Memory Issues
```
Process killed (out of memory)
```
**Solution**: 
- Upgrade to paid plan for more RAM
- Or use model quantization (see advanced config)

#### 3. Model Loading Fails
```
Could not load model
```
**Solution**: Check if `models/mask_mobilenet.h5` is in repository

#### 4. Camera Not Working
```
Camera access denied
```
**Solution**: This is normal for server deployment - camera works for local users only

## 🔄 Continuous Deployment

Render automatically deploys when you:
1. **Push to main branch**
2. **Update environment variables**
3. **Modify render.yaml**

### Deployment Process:
1. **Build**: Install dependencies
2. **Deploy**: Start the service
3. **Health Check**: Verify `/api/v1/health`
4. **Live**: Service available at your URL

## 📈 Monitoring

### Render Dashboard:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, response times
- **Events**: Deployment history
- **Health**: Service status

### Application Monitoring:
```bash
# Health check
curl https://your-app.onrender.com/api/v1/health

# Detailed health
curl https://your-app.onrender.com/api/v1/health/detailed

# Metrics
curl https://your-app.onrender.com/api/v1/metrics
```

## 🚀 Advanced Configuration

### Custom Domain:
1. **Go to Settings** in Render dashboard
2. **Add Custom Domain**
3. **Configure DNS** (CNAME record)

### SSL Certificate:
- ✅ **Automatic HTTPS** (Let's Encrypt)
- ✅ **Free SSL certificates**
- ✅ **Auto-renewal**

### Scaling:
```yaml
# In render.yaml
services:
  - type: web
    plan: standard  # More resources
    scaling:
      minInstances: 1
      maxInstances: 3
```

## 🎯 Step-by-Step Deployment

### 1. Prepare Repository
```bash
# Ensure these files exist:
# - render.yaml
# - requirements-render.txt
# - serve.py (updated)
# - models/mask_mobilenet.h5

git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Deploy to Render
1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click "New +" → "Blueprint"
4. Select your repository
5. Click "Apply"

### 3. Wait for Deployment
- **Build time**: 5-10 minutes (first time)
- **Status**: Check in Render dashboard
- **Logs**: Monitor build progress

### 4. Test Your App
```bash
# Your app will be available at:
https://mask-detection-system.onrender.com

# Test endpoints:
curl https://your-app.onrender.com/api/v1/health
```

## 🎉 What You Get

After successful deployment:

### 🌐 **Live Web Application**:
- Full mask detection interface
- Real-time camera support (for users with cameras)
- Image upload and processing
- Professional UI with Bootstrap

### 🤖 **Complete AI Features**:
- TensorFlow model fully loaded
- Accurate mask/no-mask classification
- Confidence percentages
- Face detection with bounding boxes

### 📊 **Monitoring & APIs**:
- Health check endpoints
- System metrics
- Performance monitoring
- Error tracking

### 🔒 **Production Ready**:
- HTTPS enabled
- Environment-based configuration
- Error handling
- Logging system

## 📞 Support

If you need help:
1. **Check Render logs** in dashboard
2. **Review deployment guide**
3. **Render documentation**: https://render.com/docs
4. **GitHub issues**: Create an issue

---

## 🎊 **Ready to Deploy!**

Your Mask Detection System will have **ALL features working** on Render:
- ✅ Complete ML model
- ✅ Real-time detection
- ✅ Professional interface
- ✅ Full API endpoints
- ✅ Monitoring & health checks

**Deploy now and get the complete experience!** 🚀