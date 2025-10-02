#!/usr/bin/env python3
"""
Advanced Tunnel Manager for Kagema FM
Auto-reconnect and preemptive resolution of tunnel issues
"""

import requests
import subprocess
import time
import json
import logging
import os
import signal
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tunnel_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TunnelManager')

class TunnelManager:
    def __init__(self):
        self.ngrok_api_url = "http://localhost:4040/api/tunnels"
        self.expected_tunnels = ["https", "http"]
        self.health_check_interval = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.tunnel_status = {
            "last_check": None,
            "consecutive_failures": 0,
            "last_restart": None,
            "total_restarts": 0
        }
        self.known_issues = {
            "ERR_NGROK_3200": "Tunnel connection failed",
            "ERR_NGROK_334": "Endpoint already online",
            "ERR_NGROK_105": "Authentication failed",
            "ERR_NGROK_108": "Account limit exceeded"
        }
        
    def get_tunnel_status(self) -> Dict:
        """Get current tunnel status from ngrok API"""
        try:
            response = requests.get(self.ngrok_api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "tunnels": data.get("tunnels", []),
                    "count": len(data.get("tunnels", [])),
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "tunnels": [],
                    "count": 0
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tunnels": [],
                "count": 0
            }
    
    def check_tunnel_health(self) -> Tuple[bool, str]:
        """Comprehensive tunnel health check"""
        logger.info("🔍 Checking tunnel health...")
        
        # 1. Check if ngrok process is running
        ngrok_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                          if 'ngrok' in p.info['name'].lower()]
        
        if not ngrok_processes:
            return False, "No ngrok processes found"
        
        logger.info(f"✅ Found {len(ngrok_processes)} ngrok process(es)")
        
        # 2. Check ngrok API accessibility
        status = self.get_tunnel_status()
        if not status["success"]:
            return False, f"Ngrok API not accessible: {status['error']}"
        
        # 3. Verify expected tunnels exist
        tunnels = status["tunnels"]
        if len(tunnels) == 0:
            return False, "No active tunnels found"
        
        # 4. Test tunnel connectivity
        for tunnel in tunnels:
            public_url = tunnel.get("public_url")
            if public_url and public_url.startswith("https"):
                try:
                    test_response = requests.get(public_url, timeout=10)
                    if test_response.status_code == 200:
                        logger.info(f"✅ Tunnel {public_url} is accessible")
                        return True, f"All tunnels healthy. Primary: {public_url}"
                except Exception as e:
                    logger.warning(f"⚠️ Tunnel {public_url} test failed: {e}")
        
        return False, "Tunnels exist but not accessible"
    
    def kill_existing_ngrok_processes(self):
        """Safely kill all ngrok processes"""
        logger.info("🔄 Killing existing ngrok processes...")
        
        try:
            # Kill via process name
            subprocess.run(["pkill", "-f", "ngrok"], check=False)
            time.sleep(2)
            
            # Force kill if still running
            ngrok_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                             if 'ngrok' in p.info['name'].lower()]
            
            for proc in ngrok_processes:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    logger.info(f"✅ Terminated ngrok process {proc.pid}")
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        proc.kill()
                        logger.info(f"🔫 Force killed ngrok process {proc.pid}")
                    except psutil.NoSuchProcess:
                        pass
                        
        except Exception as e:
            logger.error(f"❌ Error killing ngrok processes: {e}")
    
    def restart_expo_service(self) -> bool:
        """Restart the Expo service via supervisorctl"""
        try:
            logger.info("🔄 Restarting Expo service...")
            
            # Stop expo service
            result = subprocess.run(["supervisorctl", "stop", "expo"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.warning(f"⚠️ Stop command warning: {result.stderr}")
            
            time.sleep(3)
            
            # Kill any remaining ngrok processes
            self.kill_existing_ngrok_processes()
            
            time.sleep(2)
            
            # Start expo service
            result = subprocess.run(["supervisorctl", "start", "expo"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                logger.info("✅ Expo service restarted successfully")
                self.tunnel_status["last_restart"] = datetime.now()
                self.tunnel_status["total_restarts"] += 1
                return True
            else:
                logger.error(f"❌ Failed to start expo service: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restarting expo service: {e}")
            return False
    
    def wait_for_tunnel_ready(self, timeout: int = 120) -> Tuple[bool, str]:
        """Wait for tunnel to be ready after restart"""
        logger.info(f"⏳ Waiting for tunnel to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Wait a bit for services to start
            time.sleep(5)
            
            health_ok, health_msg = self.check_tunnel_health()
            if health_ok:
                elapsed = int(time.time() - start_time)
                logger.info(f"✅ Tunnel ready after {elapsed}s: {health_msg}")
                return True, health_msg
            
            logger.info(f"⏳ Still waiting... {health_msg}")
        
        return False, "Timeout waiting for tunnel to be ready"
    
    def handle_common_errors(self) -> bool:
        """Handle common ngrok errors proactively"""
        logger.info("🔧 Checking for common tunnel issues...")
        
        try:
            # Check supervisor logs for common errors
            result = subprocess.run(
                ["tail", "-50", "/var/log/supervisor/expo.err.log"], 
                capture_output=True, text=True, timeout=10
            )
            
            log_content = result.stdout
            
            # Check for specific error patterns
            if "ERR_NGROK_334" in log_content:
                logger.warning("⚠️ Detected ERR_NGROK_334 (endpoint already online)")
                self.kill_existing_ngrok_processes()
                return True
                
            if "ERR_NGROK_3200" in log_content:
                logger.warning("⚠️ Detected ERR_NGROK_3200 (connection failed)")
                return True
                
            if "tunnel session failed" in log_content.lower():
                logger.warning("⚠️ Detected tunnel session failure")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error checking logs: {e}")
        
        return False
    
    def auto_recover(self) -> bool:
        """Perform automatic recovery sequence"""
        logger.info("🚑 Starting auto-recovery sequence...")
        
        # Step 1: Handle common errors
        if self.handle_common_errors():
            logger.info("🔧 Handled common errors, proceeding with restart")
        
        # Step 2: Restart service
        if not self.restart_expo_service():
            logger.error("❌ Failed to restart service")
            return False
        
        # Step 3: Wait for tunnel to be ready
        ready, msg = self.wait_for_tunnel_ready()
        if not ready:
            logger.error(f"❌ Recovery failed: {msg}")
            return False
        
        # Step 4: Reset failure counter
        self.tunnel_status["consecutive_failures"] = 0
        
        logger.info("✅ Auto-recovery completed successfully")
        return True
    
    def get_current_tunnel_info(self) -> Dict:
        """Get current tunnel information"""
        status = self.get_tunnel_status()
        
        if not status["success"]:
            return {
                "healthy": False,
                "error": status["error"],
                "urls": []
            }
        
        urls = []
        for tunnel in status["tunnels"]:
            urls.append({
                "url": tunnel.get("public_url"),
                "proto": tunnel.get("proto"),
                "name": tunnel.get("name")
            })
        
        return {
            "healthy": True,
            "urls": urls,
            "tunnel_count": len(status["tunnels"])
        }
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting tunnel monitoring loop...")
        
        while True:
            try:
                self.tunnel_status["last_check"] = datetime.now()
                
                # Check tunnel health
                health_ok, health_msg = self.check_tunnel_health()
                
                if health_ok:
                    logger.info(f"✅ Tunnel health check passed: {health_msg}")
                    self.tunnel_status["consecutive_failures"] = 0
                    
                    # Log current tunnel info
                    tunnel_info = self.get_current_tunnel_info()
                    if tunnel_info["healthy"] and tunnel_info["urls"]:
                        primary_url = next((u["url"] for u in tunnel_info["urls"] 
                                          if u["proto"] == "https"), "None")
                        logger.info(f"📡 Primary URL: {primary_url}")
                
                else:
                    self.tunnel_status["consecutive_failures"] += 1
                    logger.warning(f"⚠️ Tunnel health check failed ({self.tunnel_status['consecutive_failures']}/3): {health_msg}")
                    
                    # Auto-recovery after 2 consecutive failures
                    if self.tunnel_status["consecutive_failures"] >= 2:
                        logger.warning("🚨 Triggering auto-recovery...")
                        
                        if self.auto_recover():
                            logger.info("✅ Auto-recovery successful")
                        else:
                            logger.error("❌ Auto-recovery failed")
                            # Wait longer before next attempt
                            time.sleep(60)
                
                # Wait for next check
                time.sleep(self.health_check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(10)
    
    def status_report(self) -> Dict:
        """Generate comprehensive status report"""
        tunnel_info = self.get_current_tunnel_info()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tunnel_manager_status": {
                "last_check": self.tunnel_status["last_check"].isoformat() if self.tunnel_status["last_check"] else None,
                "consecutive_failures": self.tunnel_status["consecutive_failures"],
                "last_restart": self.tunnel_status["last_restart"].isoformat() if self.tunnel_status["last_restart"] else None,
                "total_restarts": self.tunnel_status["total_restarts"]
            },
            "current_tunnels": tunnel_info,
            "health_status": "healthy" if tunnel_info["healthy"] else "unhealthy"
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kagema FM Tunnel Manager")
    parser.add_argument("--command", choices=["monitor", "status", "recover", "restart"], 
                       default="monitor", help="Command to execute")
    parser.add_argument("--interval", type=int, default=30, 
                       help="Health check interval in seconds")
    
    args = parser.parse_args()
    
    manager = TunnelManager()
    manager.health_check_interval = args.interval
    
    if args.command == "monitor":
        manager.monitor_loop()
    elif args.command == "status":
        report = manager.status_report()
        print(json.dumps(report, indent=2))
    elif args.command == "recover":
        success = manager.auto_recover()
        exit(0 if success else 1)
    elif args.command == "restart":
        success = manager.restart_expo_service()
        if success:
            ready, msg = manager.wait_for_tunnel_ready()
            print(f"Result: {msg}")
        exit(0 if success else 1)

if __name__ == "__main__":
    main()