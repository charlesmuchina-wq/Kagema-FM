# Kagema FM - Multiple Tunnel Endpoints

## 🌐 Available Access URLs

### 1. **Emergent Preview (Primary)**
- **URL**: https://fm-stabilize.preview.emergentagent.com
- **Status**: ✅ Active (Built-in)
- **Reliability**: High
- **Features**: Full platform integration

### 2. **Cloudflare Tunnel** 
- **URL**: https://childhood-copied-mile-succeed.trycloudflare.com
- **Status**: ✅ Active 
- **Reliability**: Very High
- **Features**: Fast, stable, enterprise-grade

### 3. **LocalTunnel**
- **URL**: https://kagema-fm-radio.loca.lt
- **Status**: ✅ Active
- **Reliability**: Medium
- **Features**: Custom subdomain, simple setup

### 4. **Serveo (SSH-based)**
- **URL**: https://032c00c0a2d1e4ff1e054ceedc4cad24.serveo.net
- **Status**: ✅ Active
- **Reliability**: Medium
- **Features**: SSH-based, no registration required

## 📱 QR Codes for Mobile Testing

You can generate QR codes for any of these URLs for easy mobile device testing:
- Use any QR code generator with the above URLs
- Scan with phone camera or Expo Go app

## 🔧 Management Commands

### Check Tunnel Status
```bash
# Check running tunnels
ps aux | grep -E "(cloudflared|lt|ssh)"

# View logs
tail -f /tmp/cloudflare_tunnel.log
tail -f /tmp/localtunnel.log  
tail -f /tmp/serveo.log
```

### Restart Tunnels
```bash
# Restart Cloudflare Tunnel
pkill cloudflared
nohup cloudflared tunnel --url http://localhost:3000 > /tmp/cloudflare_tunnel.log 2>&1 &

# Restart LocalTunnel
pkill lt
nohup lt --port 3000 --subdomain kagema-fm-radio > /tmp/localtunnel.log 2>&1 &

# Restart Serveo
pkill ssh
nohup ssh -o StrictHostKeyChecking=no -R kagema-fm:80:localhost:3000 serveo.net > /tmp/serveo.log 2>&1 &
```

## 🎯 Recommended Usage

1. **Development**: Use Emergent Preview (most stable)
2. **Demo/Sharing**: Use Cloudflare Tunnel (fastest)
3. **Testing**: Use LocalTunnel (custom subdomain)
4. **Backup**: Use Serveo (if others fail)

## 🔒 Security Notes

- All tunnels expose your local app to the internet
- Use HTTPS versions only for production
- LocalTunnel and Serveo are free services with limitations
- Cloudflare Tunnel is most secure for production use

---
*Generated: $(date)*
*App: Kagema FM International Radio Platform*