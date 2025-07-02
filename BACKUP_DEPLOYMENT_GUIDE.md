# 🗄️ Automatic Backup System for Streamlit Cloud

This guide explains how the automated backup system protects your data during Streamlit Cloud deployments.

## 🎯 Problem Solved

**Issue**: Streamlit Cloud uses ephemeral storage, meaning all data gets lost when the app redeploys.

**Solution**: Automatic backup and restore system that stores data in the GitHub repository itself.

## 🔧 How It Works

### 1. **Automatic Backup Creation**

- **Pre-commit Hook**: Creates backup before every Git commit
- **GitHub Actions**: Creates deployment backup when code is pushed
- **Manual Backups**: Create backups anytime through the web interface

### 2. **Automatic Data Restoration**

- **Startup Check**: App automatically checks if database is empty on startup
- **Auto-Restore**: If no data found, automatically restores from latest backup
- **Seamless Recovery**: Users see their data restored without any action needed

### 3. **Storage Location**

- Backups stored in `backups/` directory in the repository
- JSON format for easy inspection and version control
- Multiple backup versions maintained automatically

## 📋 Setup Instructions

### For New Deployments

1. **Deploy to Streamlit Cloud** as usual
2. **No additional setup required** - the system works automatically
3. **First backup**: Create one through Settings → Data Management

### For Existing Deployments

1. **Create initial backup** through the web interface
2. **Commit changes** to trigger automatic backup system
3. **Redeploy** - your data will be automatically restored

## 🖥️ Using the Backup System

### Through Web Interface

1. Go to **Settings → Data Management & Backup**
2. **Create Backup**: Click "🗄️ Create Backup"
3. **Restore Backup**: Select backup and click "🔄 Restore Backup"
4. **Auto-Restore Status**: Check if auto-restore is active

### Through Command Line

```bash
# Create a backup
python backup_system.py backup

# Create a backup with custom name
python backup_system.py backup my_backup.json

# Restore from latest backup
python backup_system.py restore

# Restore from specific backup
python backup_system.py restore my_backup.json

# Check if auto-restore is needed
python backup_system.py auto-restore
```

## ⚙️ Technical Details

### Backup Contents

Each backup includes:
- **Users**: All user accounts (passwords excluded for security)
- **Income Entries**: All income records
- **Expenses**: All expense transactions
- **Savings Goals**: All savings targets
- **Metadata**: Backup date, version, database type

### Backup Format

```json
{
  "metadata": {
    "backup_date": "2024-01-01T12:00:00",
    "version": "1.0",
    "database_type": "sqlite"
  },
  "data": {
    "users": [...],
    "income_entries": [...],
    "expenses": [...],
    "savings_goals": [...]
  }
}
```

### Security Considerations

- **Passwords**: Not included in backups for security
- **User Data**: Only includes active users
- **Repository Access**: Ensure repository is private for sensitive data

## 🔄 Deployment Workflow

### 1. Development
```
Local Changes → Git Commit → Pre-commit Hook Creates Backup
```

### 2. Deployment
```
Git Push → GitHub Actions → Creates Deployment Backup → Streamlit Cloud Redeploys
```

### 3. Recovery
```
App Starts → Checks Database → Empty? → Auto-Restore → User Sees Data
```

## 📊 Monitoring

### Backup Status Indicators

- ✅ **Green**: Latest backup available, auto-restore ready
- ⚠️ **Yellow**: No backup available, create one for protection
- ❌ **Red**: Backup system error, check logs

### Auto-Restore Status

- ✅ **Database has sufficient data**: Auto-restore not needed
- ⚠️ **Database appears empty**: Auto-restore will activate on next deployment

## 🛠️ Troubleshooting

### Common Issues

1. **Backup Creation Fails**
   - Check database connectivity
   - Ensure backup directory exists
   - Verify Python dependencies

2. **Auto-Restore Not Working**
   - Check if `latest_backup.json` exists
   - Verify backup file format
   - Review app startup logs

3. **Missing Data After Deployment**
   - Create manual backup before redeployment
   - Check backup files in repository
   - Use manual restore function

### Manual Recovery

If automatic system fails:

1. **Check Repository**: Look for backup files in `backups/` directory
2. **Manual Restore**: Use Settings → Data Management → Restore Backup
3. **Contact Support**: If all else fails, check app logs

## 📂 File Structure

```
budget_manager/
├── backup_system.py           # Main backup system
├── backups/                   # Backup storage directory
│   ├── latest_backup.json     # Latest backup (auto-restore)
│   ├── backup_20240101_*.json # Timestamped backups
│   └── deployment_*.json      # GitHub Actions backups
├── .git/hooks/pre-commit      # Auto-backup on commit
└── .github/workflows/         # GitHub Actions
    └── deploy-backup.yml      # Deployment backup workflow
```

## 🎉 Benefits

- **Zero Data Loss**: Never lose data during redeployments
- **Automatic Operation**: Works without user intervention  
- **Version Control**: Multiple backup versions maintained
- **Quick Recovery**: Fast restoration in case of issues
- **Free Solution**: Uses GitHub repository storage (no external services)

## 📞 Support

If you encounter issues:

1. Check the **Settings → Data Management** for status
2. Review **app logs** for error messages
3. Manually create backup before troubleshooting
4. Use **command line tools** for detailed diagnostics

---

**✅ Your data is now protected against deployment losses!** 