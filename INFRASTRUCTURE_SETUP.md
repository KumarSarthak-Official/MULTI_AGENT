# Infrastructure Setup Guide
## Setting Up PostgreSQL, Qdrant, and Redis

This guide will help you set up the required infrastructure services for production deployment.

---

## Option 1: Managed Services (Recommended for Production)

### 1. PostgreSQL - Supabase (Free Tier)

**Why Supabase:**
- Free tier: 500MB database
- Automatic backups
- Built-in authentication (optional)
- Easy to scale

**Setup Steps:**

1. Go to https://supabase.com
2. Click "Start your project"
3. Create account (GitHub login recommended)
4. Create new project:
   - Project name: `multi-agent-research`
   - Database password: (generate strong password)
   - Region: Choose closest to you
5. Wait 2-3 minutes for provisioning
6. Get connection string:
   - Go to Project Settings → Database
   - Copy "Connection string" (URI format)
   - Example: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`

**Update .env:**
```bash
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

---

### 2. Qdrant Cloud (Free Tier)

**Why Qdrant Cloud:**
- Free tier: 1GB storage
- Managed vector database
- No infrastructure management
- Global CDN

**Setup Steps:**

1. Go to https://cloud.qdrant.io
2. Sign up (GitHub/Google login)
3. Create new cluster:
   - Cluster name: `research-vectors`
   - Region: Choose closest to you
   - Plan: Free (1GB)
4. Wait for cluster provisioning (~2 minutes)
5. Get credentials:
   - Click on cluster name
   - Copy "Cluster URL" (e.g., `https://xxx-xxx.aws.cloud.qdrant.io:6333`)
   - Go to "API Keys" tab
   - Create new API key
   - Copy the key (starts with `qdrant_`)

**Update .env:**
```bash
QDRANT_URL=https://xxx-xxx.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=qdrant_xxxxxxxxxxxxx
```

---

### 3. Redis - Upstash (Free Tier)

**Why Upstash:**
- Free tier: 10,000 requests/day
- Serverless Redis
- Global replication
- REST API support

**Setup Steps:**

1. Go to https://upstash.com
2. Sign up (GitHub/Google login)
3. Create new database:
   - Name: `research-cache`
   - Type: Regional
   - Region: Choose closest to you
   - Plan: Free
4. Get connection details:
   - Click on database name
   - Copy "Redis URL" (format: `redis://default:[PASSWORD]@[HOST]:[PORT]`)

**Update .env:**
```bash
REDIS_URL=redis://default:[PASSWORD]@[HOST]:[PORT]
```

---

## Option 2: Docker Compose (Local Development)

If you have Docker Desktop installed, you can run all services locally:

```bash
# Start all infrastructure services
docker-compose up -d postgres redis qdrant

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f postgres
```

**Services will be available at:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Qdrant: `localhost:6333`

---

## After Setup: Initialize Database

Once PostgreSQL is configured, run migrations:

```bash
cd backend

# Create tables
uv run python create_tables.py

# Or use Alembic migrations
uv run alembic upgrade head
```

---

## Verify Connectivity

Test each service:

```bash
cd backend

# Test PostgreSQL
uv run python -c "from app.models import engine; engine.connect(); print('✓ PostgreSQL connected')"

# Test Qdrant
uv run python -c "from app.tools.vector_store import vector_store; vector_store.ensure_collection(); print('✓ Qdrant connected')"

# Test Redis
uv run python -c "import redis; from app.config import settings; r = redis.from_url(settings.REDIS_URL); r.ping(); print('✓ Redis connected')"
```

---

## Cost Summary

### Free Tier Limits:
- **Supabase**: 500MB database, 2GB bandwidth/month
- **Qdrant Cloud**: 1GB vectors, unlimited requests
- **Upstash**: 10K requests/day, 256MB storage

### When You'll Need to Upgrade:
- **Supabase**: >500MB data (~5,000 research reports)
- **Qdrant**: >1GB vectors (~50,000 document chunks)
- **Upstash**: >10K cache requests/day (~300 users/day)

**Total Cost (Free Tier): $0/month**

---

## Troubleshooting

### PostgreSQL Connection Issues:
- Check firewall allows port 5432
- Verify password is correct (no special chars issues)
- Try connection pooling: add `?sslmode=require` to URL

### Qdrant Connection Issues:
- Ensure API key is set in environment
- Check cluster is "Running" status
- Verify URL includes port `:6333`

### Redis Connection Issues:
- Check URL format is correct
- Verify password doesn't have special characters
- Try REST API endpoint if TCP fails

---

## Next Steps

1. ✅ Sign up for all three services
2. ✅ Update `.env` with connection strings
3. ✅ Run database migrations
4. ✅ Test connectivity
5. ✅ Restart backend server
6. ✅ Test document upload feature

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to git
- Use different credentials for dev/staging/prod
- Rotate API keys every 90 days
- Enable IP whitelisting in production
- Use read-only replicas for analytics

---

**Need Help?** Check the troubleshooting section or create an issue in the repo.
