# Streamlit Cloud Deployment Guide

This guide will help you deploy your Smart Budget Manager to Streamlit Cloud.

## Prerequisites

1. **GitHub Repository**: Your code needs to be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has these files:
- `app.py` (main Streamlit application)
- `requirements.txt` (dependencies)
- `.streamlit/config.toml` (Streamlit configuration)

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Set the main file path: `app.py`
6. Click "Deploy!"

### 3. Environment Variables (Optional)

If you want to optimize for cloud deployment, you can set this environment variable in Streamlit Cloud:

```
STREAMLIT_CLOUD_DEPLOYMENT=true
```

This will:
- Store database and preferences in `./data/` instead of home directory
- Optimize file paths for cloud environment
- Handle permission errors gracefully

### 4. Advanced Settings

In the Streamlit Cloud deployment settings, you can configure:

```toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

## Important Notes for Cloud Deployment

### Data Persistence
- **Local Development**: Data stored in `~/.budget_manager/`
- **Cloud Deployment**: Data stored in `./data/` (temporary, resets on redeployment)
- **Recommendation**: For production use, consider integrating with a cloud database

### Multi-User Considerations
- Current setup uses a single SQLite database
- All users share the same data in cloud deployment
- For multi-user apps, implement user authentication and separate databases

### File Permissions
- The app handles permission errors gracefully
- Falls back to current directory if home directory isn't accessible
- Creates necessary directories automatically

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   - Check that all dependencies are in `requirements.txt`
   - Ensure relative imports work correctly

2. **File Permission Errors**
   - The app has fallback mechanisms for this
   - Set `STREAMLIT_CLOUD_DEPLOYMENT=true` environment variable

3. **Database Issues**
   - Database resets on each deployment
   - Consider using Streamlit's session state for temporary data
   - For persistent data, integrate with external database services

### Testing Locally

Before deploying, test with cloud-like conditions:

```bash
# Set environment variable to simulate cloud deployment
export STREAMLIT_CLOUD_DEPLOYMENT=true
streamlit run app.py
```

## Post-Deployment

After successful deployment:

1. **Test all features** in the cloud environment
2. **Share your app** with the provided URL
3. **Monitor app performance** through Streamlit Cloud dashboard
4. **Update as needed** by pushing to your GitHub repository

## Security Considerations

- No sensitive data is stored (only budget data)
- All data is local to the app instance
- Consider adding authentication for production use
- Environment variables are handled securely

Your Smart Budget Manager is now ready for the cloud! 🚀 