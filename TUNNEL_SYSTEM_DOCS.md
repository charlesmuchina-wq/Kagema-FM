# Tunnel System Architecture - Kagema FM

## Current Tunnel System

### Emergent Platform Tunnels ✅
- **Primary URL**: https://carmedia-hub-1.preview.emergentagent.com
- **Backend API**: https://carmedia-hub-1.preview.emergentagent.com/api/
- **Frontend**: https://carmedia-hub-1.preview.emergentagent.com/
- **Monitoring**: /app/emergent_tunnel_watchdog.sh

### Configuration Files
- **Frontend Environment**: `/app/frontend/.env`
- **Supervisor Config**: `/etc/supervisor/conf.d/tunnel-watchdog.conf`
- **Monitoring Script**: `/app/emergent_tunnel_watchdog.sh`

## Legacy System (DEPRECATED) ❌

### ngrok (No longer used)
- **Legacy URL Pattern**: localhost:4040/api/tunnels
- **Legacy Scripts**: tunnel_watchdog.sh, tunnel_manager.py
- **Status**: Archived and replaced

## Troubleshooting

### Common Issues
1. **ERR_NGROK_3200**: Legacy reference issue
   - **Solution**: Ensure all configurations use Emergent tunnel URLs
   - **Validation**: Run `/app/validate_tunnel_config.py`

2. **Tunnel Health Check Failures**
   - **Check**: Monitor `/var/log/emergent_tunnel_watchdog.log`
   - **Commands**: `supervisorctl status emergent-tunnel-watchdog`

3. **Configuration Validation**
   - **Script**: `/app/validate_tunnel_config.py`
   - **Manual Check**: Verify .env files use correct URLs

### Health Monitoring
- **Watchdog Process**: `emergent-tunnel-watchdog`
- **Health Check Interval**: 60 seconds
- **Performance Check Interval**: 300 seconds (5 minutes)
- **Log Location**: `/var/log/emergent_tunnel_watchdog.log`

### Emergency Procedures
1. **Tunnel Failure Recovery**:
   ```bash
   supervisorctl restart emergent-tunnel-watchdog
   supervisorctl restart expo
   ```

2. **Configuration Reset**:
   ```bash
   /app/validate_tunnel_config.py
   supervisorctl reread
   supervisorctl update
   ```

3. **Legacy Cleanup**:
   ```bash
   /app/tunnel_system_cleanup_and_prevention.py
   ```

---
*Last Updated: 2025-10-10T04:31:55.375140*
*System Version: Emergent Platform Integration*
