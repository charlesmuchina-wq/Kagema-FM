# 📡 Dragon KARAU AI - API Reference

## Base URL

```
http://localhost:8001
```

---

## 🐉 Dragon AI Orchestrator

### GET `/api/dragon-ai/status`

**Description:** Get orchestrator status

**Response:**
```json
{
  "status": "completed",
  "current_task": null,
  "last_run": "2025-12-01T11:01:51.338730",
  "cycle_count": 1,
  "total_tasks": 7
}
```

---

### POST `/api/dragon-ai/run-tasks`

**Description:** Trigger complete maintenance cycle (7 tasks)

**Response:**
```json
{
  "cycle_number": 1,
  "started_at": "2025-12-01T11:01:08.315953",
  "tasks": [
    {
      "task_number": 1,
      "task_name": "Discovery Engine",
      "status": "success",
      "stations_discovered": 5000,
      "stations_saved": 0,
      "countries": 10
    }
  ],
  "completed_at": "2025-12-01T11:01:51.338737",
  "duration_seconds": 43.02278,
  "status": "success"
}
```

---

### GET `/api/dragon-ai/history`

**Description:** Get execution history

**Query Parameters:**
- `limit` (int, optional): Number of records to return (default: 10)

**Response:**
```json
{
  "history": [
    {
      "cycle_number": 1,
      "tasks": [...],
      "duration_seconds": 43.0
    }
  ]
}
```

---

### GET `/api/dragon-ai/test-history`

**Description:** Get UI test execution history

**Query Parameters:**
- `limit` (int, optional): Number of records to return (default: 10)

**Response:**
```json
{
  "test_history": [
    {
      "timestamp": "2025-12-01T...",
      "total_tests": 8,
      "passed_tests": 8,
      "failed_tests": 0,
      "success_rate": 100.0
    }
  ]
}
```

---

### GET `/api/dragon-ai/test-stats`

**Description:** Get UI test statistics

**Response:**
```json
{
  "total_tests": 30,
  "average_success_rate": 98.5,
  "trend": "improving",
  "last_test_time": "2025-12-01T...",
  "last_success_rate": 100.0
}
```

---

### POST `/api/dragon-ai/run-ui-tests`

**Description:** Manually trigger UI test suite

**Response:**
```json
{
  "timestamp": "2025-12-01T...",
  "status": "completed",
  "total_tests": 8,
  "passed_tests": 8,
  "failed_tests": 0,
  "success_rate": 100.0,
  "tests": {
    "globe_view": {"status": "passed"},
    "map_view": {"status": "passed"}
  }
}
```

---

### GET `/api/dragon-ai/latest-test`

**Description:** Get most recent test results

**Response:** Same as single test result from `/run-ui-tests`

---

## 🔍 Dragon Search

### GET `/api/dragon-search/stations`

**Description:** Search radio stations with filters

**Query Parameters:**
- `query` (string, optional): Search by station name
- `language` (string, optional): Filter by language code (e.g., "en")
- `genre` (string, optional): Filter by genre
- `country` (string, optional): Filter by country code (e.g., "US")
- `min_quality` (int, optional): Minimum quality score (0-100)
- `max_quality` (int, optional): Maximum quality score (0-100)
- `validated_only` (bool, optional): Only validated stations
- `limit` (int, optional): Number of results (default: 50, max: 500)
- `skip` (int, optional): Number of results to skip

**Example:**
```bash
GET /api/dragon-search/stations?country=US&min_quality=70&limit=20
```

**Response:**
```json
[
  {
    "id": "station-123",
    "name": "Cool FM",
    "country": "US",
    "language": "en",
    "genre": "Pop",
    "stream_url": "http://stream.example.com/live",
    "quality_score": 85,
    "validated": true,
    "homepage": "http://coolfm.com",
    "favicon": "http://coolfm.com/icon.png",
    "bitrate": 192
  }
]
```

---

### GET `/api/dragon-search/filters/languages`

**Description:** Get list of available languages

**Response:**
```json
{
  "languages": ["en", "es", "fr", "pt", "sw", "de", "ja", "zh"]
}
```

---

### GET `/api/dragon-search/filters/genres`

**Description:** Get list of available genres

**Response:**
```json
{
  "genres": ["Pop", "Rock", "Jazz", "Classical", "Hip Hop", ...]
}
```

---

### GET `/api/dragon-search/filters/countries`

**Description:** Get list of countries with station counts

**Response:**
```json
{
  "countries": [
    {"code": "US", "count": 45},
    {"code": "GB", "count": 32},
    {"code": "DE", "count": 28}
  ]
}
```

---

### GET `/api/dragon-search/stats`

**Description:** Get database statistics

**Response:**
```json
{
  "total_stations": 139,
  "validated_stations": 139,
  "validation_rate": "100.0%",
  "unique_languages": 8,
  "unique_countries": 28,
  "unique_genres": 75
}
```

---

## 🤖 Radio Intelligence Bot

### GET `/api/radio-intelligence/status`

**Description:** Get bot status and statistics

**Response:**
```json
{
  "status": "operational",
  "ai_enabled": false,
  "statistics": {
    "total_validations": 20,
    "broken_links_detected": 1,
    "auto_replacements": 0,
    "ai_discoveries": 0,
    "failed_validations": 0,
    "compromised_urls_detected": 2,
    "registered_stations": 139,
    "operational_stations": 14,
    "broken_stations": 1,
    "compromised_stations": 0
  }
}
```

---

### GET `/api/radio-intelligence/stations`

**Description:** Get all registered stations with health status

**Response:**
```json
{
  "stations": [
    {
      "station_id": "kagema_fm",
      "name": "Kagema FM",
      "url": "http://stream.kagema.fm/live",
      "country": "Kenya",
      "genre": "general",
      "language": "en",
      "health_status": "OPERATIONAL",
      "last_validated": "2025-12-01T...",
      "replacement_count": 0
    }
  ]
}
```

---

### POST `/api/radio-intelligence/scan`

**Description:** Scan all stations and perform auto-healing

**Response:**
```json
{
  "total_stations": 139,
  "operational": 130,
  "broken": 9,
  "compromised": 0,
  "healed": 8,
  "failed_to_heal": 1,
  "stations_details": [
    {
      "station_id": "station-1",
      "health_status": "OPERATIONAL",
      "accessible": true
    }
  ]
}
```

---

### POST `/api/radio-intelligence/validate/{station_id}`

**Description:** Validate a specific radio station

**Path Parameters:**
- `station_id` (string): Station ID to validate

**Response:**
```json
{
  "station_id": "kagema_fm",
  "health_status": "OPERATIONAL",
  "accessible": true,
  "status_code": 200,
  "validated_at": "2025-12-01T..."
}
```

---

### POST `/api/radio-intelligence/heal/{station_id}`

**Description:** Attempt to heal a broken station

**Path Parameters:**
- `station_id` (string): Station ID to heal

**Response:**
```json
{
  "status": "healed",
  "station_id": "kagema_fm",
  "new_url": "http://new-stream.kagema.fm/live",
  "confidence": 85,
  "reasoning": "Match based on country (KE) and votes (150)",
  "source": "radio_browser"
}
```

**Error Response:**
```json
{
  "status": "failed",
  "station_id": "kagema_fm",
  "message": "No suitable replacement found"
}
```

---

## 📊 Kagema FM Core APIs

### GET `/api/`

**Description:** API root and health check

**Response:**
```json
{
  "message": "Kagema FM Satellite & Offline Radio API",
  "version": "5.0.0",
  "features": [
    "satellite_connectivity",
    "offline_mode",
    "international_coverage",
    "content_compliance"
  ]
}
```

---

### GET `/api/languages`

**Description:** Get supported languages

**Response:**
```json
{
  "languages": [
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "sw", "name": "Swahili", "native_name": "Kiswahili"}
  ],
  "total_count": 8
}
```

---

## 🔒 Error Responses

All endpoints return standard HTTP status codes:

### Success (2xx)
- `200 OK` - Request successful
- `201 Created` - Resource created

### Client Errors (4xx)
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

### Server Errors (5xx)
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 📝 Notes

1. **Rate Limiting:** No rate limiting currently implemented
2. **Authentication:** No authentication required (add in production)
3. **CORS:** Enabled for all origins (`*`)
4. **Content-Type:** All responses are `application/json`
5. **Timestamps:** All timestamps are in ISO 8601 format (UTC)

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Base URL:** `http://localhost:8001`

🐉 **Dragon KARAU AI API Reference** 🐉