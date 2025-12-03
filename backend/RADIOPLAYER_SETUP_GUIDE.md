# 🔐 Radioplayer API Authentication - Complete Setup Guide

## Overview

This guide walks you through setting up **RSA-SHA256 signature-based authentication** for the Radioplayer Partner API (WRAPI) to unlock access to 500+ UK radio stations.

---

## 📋 **Current Status**

### Without Authentication (Current)
- ❌ Only 10 hardcoded UK stations
- ❌ No real-time data
- ❌ No automatic updates
- ❌ Limited metadata

### With Authentication (After Setup)
- ✅ **500+ UK radio stations**
- ✅ Real-time stream URLs
- ✅ High-quality logos & metadata
- ✅ Programme schedules
- ✅ Automatic updates

---

## 🚀 **Setup Steps**

### **STEP 1: Apply for Radioplayer API Access**

1. **Contact Radioplayer:**
   - Website: https://developers.radioplayer.org
   - Email: developers@radioplayer.org (or via contact form)
   
2. **Request Access to:**
   - Partner API (WRAPI)
   - API Key (keyId)
   - Private RSA Key

3. **Provide Information:**
   ```
   Company/App Name: Dragon KARAU AI
   Purpose: Global radio aggregation and streaming platform
   Target Audience: Worldwide radio listeners
   Expected Usage: Station metadata, stream URLs, logos, schedules
   Geographic Focus: UK radio stations initially
   Monthly API Calls: ~10,000 (estimated)
   ```

4. **Expected Response Time:** 3-7 business days

---

### **STEP 2: Receive Credentials**

You will receive:

1. **API Key (keyId)**
   - Example format: `your-api-key-12345`
   - Used to identify your application

2. **Private RSA Key (PEM format)**
   - File: `private_key.pem` OR string in email
   - Used to sign API requests
   - **KEEP THIS SECRET!**

---

### **STEP 3: Add Credentials to Environment**

#### Option A: Using PEM File

1. Save the private key file to `/app/backend/radioplayer_private_key.pem`

2. Add to `/app/backend/.env`:
```bash
# Radioplayer API Authentication
RADIOPLAYER_API_KEY=your-api-key-12345
RADIOPLAYER_PRIVATE_KEY_PATH=/app/backend/radioplayer_private_key.pem
```

#### Option B: Using PEM String (Recommended for Docker)

Add to `/app/backend/.env`:
```bash
# Radioplayer API Authentication
RADIOPLAYER_API_KEY=your-api-key-12345
RADIOPLAYER_PRIVATE_KEY_PEM="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...your-key-content...
...multiple lines...
-----END RSA PRIVATE KEY-----"
```

**Note:** Make sure to keep the quotes and newlines intact for the PEM string.

---

### **STEP 4: Restart Backend**

```bash
sudo supervisorctl restart backend
```

---

### **STEP 5: Test Authentication**

#### Check Auth Status
```bash
curl http://localhost:8001/api/radioplayer/auth-status | jq '.'
```

**Expected Response (Configured):**
```json
{
  "status": "success",
  "data": {
    "configured": true,
    "api_key_present": true,
    "private_key_loaded": true,
    "api_key_preview": "your-api..."
  }
}
```

#### Test Fetching Stations
```bash
curl -X POST http://localhost:8001/api/radioplayer/test-fetch | jq '.'
```

**Expected Response (Success):**
```json
{
  "status": "success",
  "data": {
    "source": "radioplayer",
    "authenticated": true,
    "discovered": 500,
    "saved": 500,
    "duplicates": 0
  }
}
```

---

## 🔧 **Technical Details**

### Authentication Method

**Type:** RSA-SHA256 Signature-based Authentication

**Process:**
1. Generate RFC 2822 date string
2. Create signature string: `(request-target): get /path\ndate: Wed, 03 Dec 2025 21:39:00 GMT`
3. Sign using RSA private key with SHA256
4. Encode signature as Base64
5. Add to Authorization header

**Request Headers:**
```
Date: Wed, 03 Dec 2025 21:39:00 GMT
Authorization: Signature keyId="your-key",algorithm="rsa-sha256",headers="(request-target) date",signature="base64-signature"
User-Agent: DragonKarauAI/1.0
Accept: application/json
```

---

## 📊 **What Gets Fetched**

### Station Data Structure

From Radioplayer API:
```json
{
  "stations": [
    {
      "rpId": "bbcradio1",
      "name": "BBC Radio 1",
      "description": "New music and entertainment",
      "logo": "https://cdn.radioplayer.co.uk/logos/bbcradio1.png",
      "country": "GB",
      "streamUrl": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one",
      "format": "Pop, Rock",
      "website": "https://www.bbc.co.uk/radio1"
    }
  ]
}
```

Stored in Dragon KARAU AI Database:
```json
{
  "name": "BBC Radio 1",
  "stream_url": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one",
  "country": "GB",
  "language": "en",
  "genre": "Pop, Rock",
  "description": "New music and entertainment",
  "logo_url": "https://cdn.radioplayer.co.uk/logos/bbcradio1.png",
  "website": "https://www.bbc.co.uk/radio1",
  "radioplayer_id": "bbcradio1",
  "source": "radioplayer",
  "last_updated": "2025-06-01T12:00:00Z"
}
```

---

## 🔒 **Security Best Practices**

1. ✅ **Never commit private keys to Git**
   - Add `radioplayer_private_key.pem` to `.gitignore`
   - Use environment variables for production

2. ✅ **Rotate keys periodically**
   - Request new keys every 6-12 months
   - Update `.env` with new credentials

3. ✅ **Monitor API usage**
   - Check logs for 401 errors (authentication failures)
   - Track rate limits

4. ✅ **Use file permissions**
   ```bash
   chmod 600 /app/backend/radioplayer_private_key.pem
   ```

---

## 🐛 **Troubleshooting**

### Problem: "configured: false"

**Solution:**
- Check if `RADIOPLAYER_API_KEY` is set in `.env`
- Check if `RADIOPLAYER_PRIVATE_KEY_PEM` or `RADIOPLAYER_PRIVATE_KEY_PATH` is set
- Restart backend: `sudo supervisorctl restart backend`

### Problem: "401 Unauthorized"

**Possible Causes:**
1. Invalid API key
2. Private key doesn't match API key
3. Signature generation error
4. Date header format incorrect

**Solution:**
- Verify credentials with Radioplayer
- Check private key format (must be valid PEM)
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

### Problem: "No stations fetched"

**Solution:**
- Test authentication endpoint first
- Check if API endpoint URL is correct
- Verify Radioplayer API is operational
- Check backend logs for detailed errors

---

## 📞 **Support**

### Radioplayer Support
- Developer Hub: https://developers.radioplayer.org
- Email: developers@radioplayer.org
- Documentation: https://developers.radioplayer.org/docs

### Dragon KARAU AI Support
- API Status: `GET /api/radioplayer/auth-status`
- Test Fetch: `POST /api/radioplayer/test-fetch`
- Backend Logs: `tail -f /var/log/supervisor/backend.err.log`

---

## 🎯 **Next Steps After Setup**

1. ✅ Verify authentication works
2. ✅ Fetch all UK stations (500+)
3. ✅ Integrate with automated crawler (runs every 12 hours)
4. ✅ Enable automatic geocoding for new stations
5. ✅ Test "nearest stations" feature with UK locations
6. ✅ Monitor for stream URL updates

---

## 📈 **Expected Results**

### Before Authentication
- UK Stations: 10 (hardcoded)
- Data Quality: Limited
- Updates: Manual only

### After Authentication
- UK Stations: **500+** (from API)
- Data Quality: **Official, high-quality**
- Updates: **Automatic every 12 hours**
- Additional Benefits:
  - Station logos (high-res)
  - Programme schedules
  - Accurate metadata
  - Working stream URLs
  - Automatic healing

---

## ✅ **Implementation Checklist**

- [ ] Applied for Radioplayer API access
- [ ] Received API Key and Private Key
- [ ] Added credentials to `/app/backend/.env`
- [ ] Restarted backend service
- [ ] Tested authentication status (configured: true)
- [ ] Successfully fetched stations from API
- [ ] Verified stations saved to database
- [ ] Enabled automated crawler for Radioplayer
- [ ] Tested nearest stations feature with UK locations

---

**Status:** 🟡 **Ready for Credentials** 

Once you receive API credentials from Radioplayer, follow Steps 3-5 to complete setup.

**Estimated Setup Time:** 15 minutes (after receiving credentials)

**ROI:** 5,000% increase in UK station coverage (10 → 500+)
