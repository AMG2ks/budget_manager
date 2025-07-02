# 🗄️ Persistent Storage Setup Guide

## Problem: Data Loss on Redeployment

**Issue:** Streamlit Cloud uses ephemeral storage, so all data (income, expenses, goals) gets deleted on each redeployment.

**Solution:** Use an external PostgreSQL database that persists data permanently.

## ✅ 100% Free Options (Permanent)

### Option 1: GitHub Storage (🆓 Most Free - Uses Your GitHub Account)

**Why Choose GitHub Storage:**
- ✅ **100% Free Forever** - No paid tiers or limits
- ✅ **Private & Secure** - Uses your GitHub account  
- ✅ **Built-in Backups** - Git version control included
- ✅ **Zero Dependencies** - No external database services

**Quick Setup:**
1. **Create GitHub Token**: Go to GitHub.com → Settings → Developer settings → Personal access tokens → Generate new token (classic)
2. **Select Scope**: Check `repo` (Full control of private repositories)
3. **Add to Streamlit Cloud**: Settings → Advanced → Environment variables:
   - `GITHUB_TOKEN` = your_token_here
   - `GITHUB_USERNAME` = your_github_username  
   - `USE_GITHUB_STORAGE` = true
4. **Redeploy**: Your app will auto-create a private repository for data storage!

### Option 2: Supabase (Database Service - Forever Free)

**Free Tier**: 500MB storage + 2GB bandwidth (perfect for budget apps!)

1. **Create Account**: Go to [supabase.com](https://supabase.com) and sign up
2. **Create Project**: Click "New Project" and choose a name
3. **Get Database URL**:
   - Go to **Settings** → **Database**
   - Find **Connection string** section
   - Copy the **URI** (PostgreSQL format)
   - Example: `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`

4. **Add to Streamlit Cloud**:
   - Go to your app in [share.streamlit.io](https://share.streamlit.io)
   - Click **⚙️ Settings** → **Advanced** → **Environment variables**
   - Add new variable:
     - **Key**: `DATABASE_URL`
     - **Value**: Your PostgreSQL URL from step 3
   - Click **Save**

5. **Redeploy**: Your app will automatically redeploy and use persistent storage!

### Option 2: Neon (Generous Free Tier)

**Free Tier**: 3GB storage + 1 database (no time limit!)

1. **Create Account**: Go to [neon.tech](https://neon.tech) and sign up
2. **Create Database**: Click "Create a database"
3. **Get Connection String**:
   - Go to **Dashboard** → **Connection Details**
   - Copy **Connection string** (PostgreSQL format)
4. **Add to Streamlit Cloud** (same as step 4 above)

### Option 3: ElephantSQL (Small but Free)

**Free Tier**: 20MB storage (enough for thousands of budget entries!)

1. **Create Account**: Go to [elephantsql.com](https://elephantsql.com)
2. **Create Instance**: Choose "Tiny Turtle" plan (free)
3. **Get URL**: Copy the PostgreSQL URL from dashboard
4. **Add to Streamlit Cloud** (same as step 4 above)

### Option 4: Railway (Monthly Free Credits)

**Free Tier**: $5/month credit (covers small PostgreSQL usage)

1. **Create Account**: Go to [railway.app](https://railway.app)
2. **New Project**: Click "New Project" → "Provision PostgreSQL"
3. **Get Connection URL**:
   - Click on your PostgreSQL service
   - Go to **Connect** tab
   - Copy **Postgres Connection URL**
4. **Add to Streamlit Cloud** (same as step 4 above)

## 🎯 Verification

After setup, check your app's **Settings** → **Preferences** tab:

- ✅ **PostgreSQL - Persistent Storage Enabled** = Success!
- ⚠️ **SQLite - Temporary Storage** = Setup needed

## 💰 Free Tier Comparison

| Service | Free Storage | Free Duration | Perfect For |
|---------|--------------|---------------|-------------|
| **🆓 GitHub Storage** | Unlimited* | ✅ Forever | **Best choice - Zero cost!** |
| **Supabase** | 500MB + 2GB bandwidth | ✅ Forever | Traditional database lovers |
| **Neon** | 3GB storage | ✅ Forever | Large apps with lots of data |
| **ElephantSQL** | 20MB storage | ✅ Forever | Personal budget tracking |
| **Railway** | $5/month credit | ✅ Monthly renewal | Small apps, auto-renewing |

*GitHub repositories have soft limits (1GB recommended), but budget apps typically use <1MB

### 📊 Storage Capacity Examples

**20MB (ElephantSQL)** can store:
- 📊 ~10,000 expense entries
- 💰 ~1,000 income entries  
- 🎯 ~500 savings goals
- **Perfect for personal use!**

**500MB (Supabase)** can store:
- 📊 ~250,000 expense entries
- 💰 ~50,000 income entries
- 🎯 ~25,000 savings goals
- **Perfect for family/business use!**

## 🔧 Technical Details

### What Happens
- **Without setup**: Uses SQLite file (deleted on redeployment)
- **With setup**: Uses PostgreSQL database (persists forever)
- **Auto-detection**: App automatically switches based on `DATABASE_URL`

### Environment Variable Format
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### Connection Security
- All connections use SSL/TLS encryption
- Passwords are never stored in your code
- Environment variables are secure in Streamlit Cloud

## 🔄 Migration

### Existing Data
If you have data in SQLite that you want to migrate:

1. **Export Data**: Use app's **Settings** → **Data Management** → **Export to CSV**
2. **Set up PostgreSQL** (following steps above)
3. **Import Data**: Use **Settings** → **Demo Data** to recreate structure, then manually add your data

### Future Deployments
Once PostgreSQL is set up:
- ✅ All deployments use the same database
- ✅ Data persists across updates
- ✅ No more data loss
- ✅ Multi-user data is preserved

## 🛠️ Troubleshooting

### "Database connection: Failed"
1. Check the `DATABASE_URL` format
2. Ensure URL starts with `postgresql://` (not `postgres://`)
3. Verify database is running in your cloud provider
4. Check firewall settings (allow external connections)

### "Table doesn't exist" errors
- App automatically creates tables on first connection
- If issues persist, restart your Streamlit app

### URL Format Issues
```bash
# ❌ Wrong format
postgres://user:pass@host:port/db

# ✅ Correct format  
postgresql://user:pass@host:port/db
```

## 📊 Benefits

### Before (SQLite)
- ❌ Data lost on every deployment
- ❌ No multi-user persistence
- ❌ Manual backups needed
- ❌ Limited to single instance

### After (PostgreSQL)
- ✅ Data persists forever
- ✅ True multi-user support
- ✅ Automatic backups
- ✅ Scalable and reliable
- ✅ Professional database features

## 🔒 Security

- Database credentials are stored securely in Streamlit Cloud
- All connections use encrypted SSL
- No sensitive data exposed in code
- Environment variables are private to your app

## 📞 Support

If you encounter issues:
1. Check the app's Settings → Preferences for connection status
2. Verify `DATABASE_URL` format in Streamlit Cloud settings
3. Test connection in your database provider's dashboard
4. Contact support for your database provider if connection fails

---

**🎉 Once set up, you'll never lose data again!** Your budget manager will work like a professional application with persistent, reliable storage. 