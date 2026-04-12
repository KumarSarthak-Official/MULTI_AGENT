# Quick Start Guide - Infrastructure Setup

## 🚀 What We've Built

You now have:
- ✅ Complete database models (User, Research, Document)
- ✅ Alembic migrations ready
- ✅ Redis caching with graceful fallback
- ✅ Qdrant Cloud support
- ✅ LLM response caching (reduces API costs)

## 📋 What You Need to Do

### Step 1: Sign Up for Managed Services (15 minutes)

**All services have generous free tiers - $0/month to start!**

#### A. Supabase (PostgreSQL)
1. Go to https://supabase.com
2. Sign up with GitHub
3. Create project: `multi-agent-research`
4. Copy connection string from Settings → Database
5. Format: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`

#### B. Qdrant Cloud (Vector Database)
1. Go to https://cloud.qdrant.io
2. Sign up with GitHub
3. Create cluster: `research-vectors` (Free tier)
4. Copy cluster URL: `https://xxx.aws.cloud.qdrant.io:6333`
5. Create API key in "API Keys" tab

#### C. Upstash (Redis)
1. Go to https://upstash.com
2. Sign up with GitHub
3. Create database: `research-cache` (Regional, Free)
4. Copy Redis URL: `redis://default:[PASSWORD]@[HOST]:[PORT]`

### Step 2: Update Your .env File

Open `.env` and update these lines:

```bash
# PostgreSQL (from Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres

# Qdrant Cloud
QDRANT_URL=https://xxx-xxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=qdrant_xxxxxxxxxxxxx

# Redis (from Upstash)
REDIS_URL=redis://default:[PASSWORD]@[HOST]:[PORT]
```

### Step 3: Initialize Database

```bash
cd backend

# Create all tables
uv run python create_tables.py

# Or use migrations
uv run alembic upgrade head
```

### Step 4: Verify Everything Works

```bash
cd backend

# Run verification script
uv run python verify_infrastructure.py
```

You should see:
```
✅ PostgreSQL: Connected successfully
✅ Qdrant: Connected successfully
✅ Redis: Connected successfully

🎉 All services are ready!
```

### Step 5: Restart Your Application

```bash
# Stop current backend (Ctrl+C)

# Start with new infrastructure
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend should still be running on port 3000
```

### Step 6: Test RAG Features

1. Open http://localhost:3000
2. Click "Show" under "Upload Documents"
3. Upload a PDF file
4. Submit a research query
5. Watch the agents work with both web search AND your documents!

## 🎯 What This Enables

**Before (without infrastructure):**
- ❌ No document upload
- ❌ No RAG retrieval
- ❌ No data persistence
- ❌ Slow (no caching)

**After (with infrastructure):**
- ✅ Upload PDFs and search them
- ✅ RAG agent retrieves relevant chunks
- ✅ All research saved to database
- ✅ LLM responses cached (faster + cheaper)
- ✅ User quota tracking ready
- ✅ Production-ready persistence

## 💰 Cost

**Free Tier Limits:**
- Supabase: 500MB database
- Qdrant: 1GB vectors
- Upstash: 10K requests/day

**You won't pay anything until you exceed these limits!**

## 🆘 Troubleshooting

### "Connection refused" errors
- Make sure you copied the full connection strings
- Check for typos in passwords
- Verify services are "Running" in their dashboards

### "Authentication failed"
- Double-check API keys are correct
- Ensure no extra spaces in .env file
- Try regenerating the API key

### Database migration fails
- Ensure PostgreSQL is connected first
- Check DATABASE_URL format is correct
- Try `uv run python create_tables.py` instead

## 📚 Need More Help?

- Full guide: `INFRASTRUCTURE_SETUP.md`
- Production readiness: `PRODUCTION_READINESS.md`
- Project docs: `CLAUDE.md`

---

**Estimated Time:** 15-20 minutes total

**Next:** Once infrastructure is working, we'll tackle Option B (Security) or Option C (Code Quality)
