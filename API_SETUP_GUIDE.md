# 🔑 Dragon KARAU AI Radio - API Keys Setup Guide

This guide will help you set up API keys for all features. **The app works without any API keys**, but adding them unlocks enhanced functionality.

---

## 📋 Quick Start

1. Copy `.env.example` to `.env` in the backend folder
2. Add only the API keys you need
3. Restart the backend: `sudo supervisorctl restart backend`
4. Features activate automatically when keys are detected

---

## 🗺️ Map & Traffic APIs (Highly Recommended)

### Option 1: TomTom (Best for Traffic) ⭐ RECOMMENDED

**Free Tier:** 2,500 requests/day + 50,000 map tiles/day

**Setup:**
1. Go to [TomTom Developer Portal](https://developer.tomtom.com/)
2. Create free account
3. Navigate to "Dashboard" → "API Keys"
4. Click "Create API Key"
5. Copy the key

**Add to `.env`:**
```bash
TOMTOM_API_KEY=your_key_here
```

**Features Unlocked:**
- ✅ Real-time traffic incidents
- ✅ Traffic flow visualization
- ✅ Accurate delay estimates
- ✅ Construction & accident alerts

---

### Option 2: Google Maps Platform

**Free Tier:** $200/month credit (typically 28,000+ requests)

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable "Maps SDK", "Places API", "Geocoding API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Restrict key to your app (recommended)

**Add to `.env`:**
```bash
GOOGLE_MAPS_API_KEY=your_key_here
```

**Features Unlocked:**
- ✅ Familiar Google Maps interface
- ✅ Built-in traffic layer
- ✅ Places integration
- ✅ Excellent geocoding

**Note:** Billing must be enabled, but you won't be charged unless you exceed $200/month

---

### Option 3: Mapbox

**Free Tier:** 50,000 requests/month

**Setup:**
1. Go to [Mapbox](https://account.mapbox.com/)
2. Sign up for free account
3. Go to "Access Tokens"
4. Copy your default public token or create new one

**Add to `.env`:**
```bash
MAPBOX_ACCESS_TOKEN=your_token_here
```

**Features Unlocked:**
- ✅ Beautiful custom map styles
- ✅ High-performance rendering
- ✅ Geocoding API
- ✅ Directions API

---

## 🎵 Now Playing Metadata APIs

### Last.fm API (Recommended for Metadata)

**Free Tier:** Unlimited (rate limited)

**Setup:**
1. Go to [Last.fm API](https://www.last.fm/api/account/create)
2. Create API account
3. Fill in application details
4. Copy API Key and Shared Secret

**Add to `.env`:**
```bash
LASTFM_API_KEY=your_api_key_here
LASTFM_SHARED_SECRET=your_secret_here
```

**Features Unlocked:**
- ✅ Song identification
- ✅ Artist information
- ✅ Album artwork
- ✅ Similar tracks suggestions

---

### Spotify API (Enhanced Metadata)

**Free Tier:** Generous (25,000+ requests/day)

**Setup:**
1. Go to [Spotify for Developers](https://developer.spotify.com/dashboard)
2. Log in with Spotify account
3. Click "Create App"
4. Fill in app details
5. Copy Client ID and Client Secret

**Add to `.env`:**
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**Features Unlocked:**
- ✅ High-quality album art
- ✅ Detailed track metadata
- ✅ Artist bio and images
- ✅ Playlist integration potential

---

## 🤖 AI Enhancement (Optional)

### OpenAI API

**Pricing:** Pay-as-you-go (starts at $5 credit)

**Setup:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and add payment method
3. Navigate to "API Keys"
4. Create new secret key

**Add to `.env`:**
```bash
OPENAI_API_KEY=sk-...your_key_here
```

**Features Unlocked:**
- ✅ Enhanced search understanding
- ✅ Better traffic announcement generation
- ✅ Smart playlist creation
- ✅ Content recommendations

---

## 🛰️ Satellite Radio (Future Feature)

### SPOT Satellite

**Status:** Research & development phase

**Notes:**
- Requires specialized satellite radio API
- Currently investigating providers
- Will update when available

---

## ✅ Verification

After adding API keys, verify they work:

### Backend Test:
```bash
curl http://localhost:8001/api/map/config
```

Look for `"enabled": true` next to your configured providers.

### Frontend Test:
1. Open app → Navigate to Map screen
2. Check traffic incidents load (if TomTom configured)
3. Verify map displays correctly

---

## 🔒 Security Best Practices

1. **Never commit `.env` to Git**
   - Already in `.gitignore`
   - Use `.env.example` for templates

2. **Restrict API Keys**
   - Add domain restrictions (Google)
   - Add app restrictions (if available)
   - Rotate keys periodically

3. **Monitor Usage**
   - Set up quota alerts
   - Check dashboards weekly
   - Stay within free tiers

4. **Environment-Specific Keys**
   - Development keys for testing
   - Production keys for live app
   - Never mix them

---

## 💰 Cost Estimates (Free Tiers)

| Provider | Free Tier | Typical Usage | Cost if Exceeded |
|----------|-----------|---------------|------------------|
| TomTom | 2,500 req/day | ~1,500/day | $0.50 per 1000 |
| Google Maps | $200 credit/mo | ~$50-100/mo | Pay-as-you-go |
| Mapbox | 50,000 req/mo | ~20,000/mo | $0.50 per 1000 |
| Last.fm | Unlimited | N/A | Always free |
| Spotify | 25,000 req/day | ~5,000/day | Always free |
| OpenAI | $5 credit | ~$2-5/mo | $0.002/1K tokens |

**Most apps stay within free tiers!**

---

## 🆘 Troubleshooting

### "API key not working"
- Check for typos in `.env`
- Restart backend: `sudo supervisorctl restart backend`
- Verify key is active in provider dashboard

### "Traffic not showing"
- TomTom key required for live traffic
- Check `TOMTOM_API_KEY` in `.env`
- Verify location permissions granted

### "Map not loading"
- OpenStreetMap works without keys
- Check internet connection
- Verify firewall/proxy settings

### "Quota exceeded"
- Check provider dashboard
- Upgrade to paid tier if needed
- Or wait for quota reset (usually daily/monthly)

---

## 📞 Support

**Provider Support:**
- TomTom: [Support Portal](https://developer.tomtom.com/support)
- Google Maps: [Support Center](https://cloud.google.com/support)
- Mapbox: [Help Center](https://support.mapbox.com/)

**App Issues:**
- Check logs: `/app/backend` and `/app/frontend`
- Verify environment variables loaded
- Test with demo data first (no keys needed)

---

## 🎯 Recommended Setup for Different Use Cases

### **Personal/Testing:**
- ✅ OpenStreetMap (no keys needed)
- ✅ Demo traffic data
- Total cost: **$0/month**

### **Small Radio Station:**
- ✅ TomTom (free tier)
- ✅ Last.fm (free)
- ✅ OpenStreetMap
- Total cost: **$0/month**

### **Medium Radio Station:**
- ✅ Google Maps ($200 credit)
- ✅ TomTom (free tier)
- ✅ Spotify + Last.fm
- Total cost: **$0-50/month**

### **Professional/Large Scale:**
- ✅ Google Maps (paid)
- ✅ TomTom (paid)
- ✅ All metadata APIs
- ✅ OpenAI enhancements
- Total cost: **$100-300/month**

---

## 🚀 Ready to Deploy!

Once you've added your preferred API keys:

1. ✅ Test locally
2. ✅ Verify all features work
3. ✅ Monitor usage dashboards
4. ✅ Deploy with confidence!

**Remember:** The app works great even without any API keys. Add them as you need enhanced features!

---

*Last Updated: January 2025*
*Dragon KARAU AI Radio v5.0.0*
