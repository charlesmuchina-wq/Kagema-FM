# 🚀 Dragon KARAU AI - Quick Start Guide

## ⚡ 5-Minute Setup

### **Step 1: Verify System is Running**

```bash
# Check backend
curl http://localhost:8001/api/
# Expected: {"message": "Kagema FM Satellite & Offline Radio API", ...}

# Check Dragon AI
curl http://localhost:8001/api/dragon-ai/status
# Expected: {"status": "idle" or "completed", ...}
```

### **Step 2: View Current Database**

```bash
# Station count
curl http://localhost:8001/api/dragon-search/stats
# Expected: {"total_stations": 139, "validation_rate": "100.0%", ...}

# Or via MongoDB
mongosh mongodb://localhost:27017/kagema_fm_db --eval "db.radio_stations.countDocuments({})"
```

### **Step 3: Run Your First Maintenance Cycle**

```bash
# Trigger all 7 automated tasks
curl -X POST http://localhost:8001/api/dragon-ai/run-tasks

# This will take ~30-60 seconds
# Watch progress in logs
tail -f /var/log/supervisor/backend.err.log | grep "Dragon AI"
```

### **Step 4: View Results**

```bash
# Get execution history
curl http://localhost:8001/api/dragon-ai/history?limit=1 | python -m json.tool

# Check UI test results
curl http://localhost:8001/api/dragon-ai/latest-test | python -m json.tool
```

---

## 🔥 Common Tasks

### **Discover New Stations**

```bash
cd /app/backend
python multi_source_crawler.py
```

### **Validate All Stations**

```bash
cd /app/backend
python relaxed_station_validator.py
```

### **Search for Stations**

```bash
# Search by country
curl "http://localhost:8001/api/dragon-search/stations?country=US&limit=10"

# Search by language
curl "http://localhost:8001/api/dragon-search/stations?language=en&limit=10"

# Search by quality
curl "http://localhost:8001/api/dragon-search/stations?min_quality=80&limit=10"
```

### **Monitor Radio Health**

```bash
# Get bot status
curl http://localhost:8001/api/radio-intelligence/status

# Scan all stations
curl -X POST http://localhost:8001/api/radio-intelligence/scan

# Validate specific station
curl -X POST http://localhost:8001/api/radio-intelligence/validate/station_id
```

### **Run Tests**

```bash
# Run UI tests
curl -X POST http://localhost:8001/api/dragon-ai/run-ui-tests

# Get test statistics
curl http://localhost:8001/api/dragon-ai/test-stats
```

---

## 📊 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/api/dragon-ai/status` | GET | Orchestrator status |
| `/api/dragon-ai/run-tasks` | POST | Trigger maintenance |
| `/api/dragon-ai/history` | GET | Execution history |
| `/api/dragon-search/stations` | GET | Search stations |
| `/api/dragon-search/stats` | GET | Database stats |
| `/api/radio-intelligence/status` | GET | Bot status |
| `/api/radio-intelligence/scan` | POST | Scan all stations |

---

## 🛠️ Troubleshooting

### **Backend not responding?**
```bash
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.err.log
```

### **No stations in database?**
```bash
cd /app/backend
python multi_source_crawler.py
python relaxed_station_validator.py
```

### **Orchestrator not running?**
```bash
curl -X POST http://localhost:8001/api/dragon-ai/run-tasks
```

---

## 🎯 Next Steps

1. ✅ **You're all set!** The system is running autonomously
2. 📅 **Daily maintenance** runs automatically at 3:00 AM
3. 🔍 **Monitor** via API endpoints
4. 📈 **Expand** the station database by running crawler
5. 🎨 **Customize** by editing Python files in `/app/backend/`

---

**Full Documentation:** See `DRAGON_KARAU_AI_GUIDE.md`

🐉 **Dragon KARAU AI is READY!** 🐉