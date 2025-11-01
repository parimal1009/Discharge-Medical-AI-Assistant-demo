# Deployment Checklist

## Pre-Deployment Checklist

### ✅ Development Environment
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Application runs successfully locally
- [ ] All tests pass (`pytest tests/`)
- [ ] No errors in logs (`logs/system.log`)

### ✅ Code Quality
- [ ] Code follows PEP 8 standards
- [ ] All functions have docstrings
- [ ] No hardcoded credentials
- [ ] Error handling implemented
- [ ] Logging configured properly

### ✅ Security
- [ ] API keys in `.env` (not in code)
- [ ] `.gitignore` includes `.env` and sensitive files
- [ ] Input validation on all endpoints
- [ ] CORS configured appropriately
- [ ] Medical disclaimers present

### ✅ Testing
- [ ] Patient retrieval works
- [ ] RAG search returns results
- [ ] Agent handoff functions
- [ ] UI displays correctly
- [ ] Error messages are user-friendly

## Production Deployment Steps

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3-pip -y

# Install nginx (optional, for reverse proxy)
sudo apt install nginx -y
```

### Step 2: Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/medical-ai
cd /opt/medical-ai

# Clone/copy application files
# (Upload your project files here)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

```bash
# Create production .env
nano .env
```

Add production settings:
```env
GROQ_API_KEY=your_production_key
TAVILY_API_KEY=your_production_key
HOST=0.0.0.0
PORT=8000
RELOAD=False
LOG_LEVEL=INFO
```

### Step 4: Systemd Service (Linux)

Create service file:
```bash
sudo nano /etc/systemd/system/medical-ai.service
```

Add content:
```ini
[Unit]
Description=Medical AI Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/medical-ai
Environment="PATH=/opt/medical-ai/venv/bin"
ExecStart=/opt/medical-ai/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable medical-ai
sudo systemctl start medical-ai
sudo systemctl status medical-ai
```

### Step 5: Nginx Reverse Proxy (Optional)

Create nginx config:
```bash
sudo nano /etc/nginx/sites-available/medical-ai
```

Add content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/medical-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Step 7: Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

## Post-Deployment Verification

### ✅ Functionality Tests
- [ ] Application accessible via domain/IP
- [ ] Homepage loads correctly
- [ ] Chat interface responsive
- [ ] Patient retrieval works
- [ ] Medical queries answered
- [ ] Sources displayed
- [ ] No console errors

### ✅ Performance Tests
- [ ] Response time < 5 seconds
- [ ] No memory leaks
- [ ] CPU usage reasonable
- [ ] Logs rotating properly

### ✅ Security Tests
- [ ] HTTPS enabled
- [ ] API keys not exposed
- [ ] CORS configured
- [ ] No sensitive data in logs

## Monitoring Setup

### Log Monitoring

```bash
# View logs
sudo journalctl -u medical-ai -f

# View application logs
tail -f /opt/medical-ai/logs/system.log
```

### Health Check Script

Create `health_check.sh`:
```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/status)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is down"
    exit 1
fi
```

Add to crontab:
```bash
*/5 * * * * /opt/medical-ai/health_check.sh
```

### Resource Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Monitor in real-time
htop
```

## Backup Strategy

### Database Backup

```bash
# Backup patient data
cp /opt/medical-ai/data/patient_reports.json \
   /opt/medical-ai/backups/patient_reports_$(date +%Y%m%d).json

# Backup vector store
tar -czf /opt/medical-ai/backups/vector_store_$(date +%Y%m%d).tar.gz \
   /opt/medical-ai/data/vector_store/
```

### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/medical-ai/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data
cp /opt/medical-ai/data/patient_reports.json \
   $BACKUP_DIR/patient_reports_$DATE.json

# Backup vector store
tar -czf $BACKUP_DIR/vector_store_$DATE.tar.gz \
   /opt/medical-ai/data/vector_store/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Add to crontab:
```bash
0 2 * * * /opt/medical-ai/backup.sh
```

## Rollback Plan

### Quick Rollback

```bash
# Stop service
sudo systemctl stop medical-ai

# Restore from backup
cp /opt/medical-ai/backups/patient_reports_YYYYMMDD.json \
   /opt/medical-ai/data/patient_reports.json

tar -xzf /opt/medical-ai/backups/vector_store_YYYYMMDD.tar.gz \
   -C /opt/medical-ai/data/

# Start service
sudo systemctl start medical-ai
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u medical-ai -n 50

# Check permissions
ls -la /opt/medical-ai

# Test manually
cd /opt/medical-ai
source venv/bin/activate
python run.py
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart medical-ai

# Consider increasing swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Database Issues

```bash
# Regenerate patient database
rm /opt/medical-ai/data/patient_reports.json
sudo systemctl restart medical-ai

# Rebuild vector store
rm -rf /opt/medical-ai/data/vector_store
sudo systemctl restart medical-ai
```

## Maintenance Schedule

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor disk space

### Weekly
- [ ] Review all logs
- [ ] Check backup integrity
- [ ] Update dependencies (if needed)

### Monthly
- [ ] Security updates
- [ ] Performance review
- [ ] User feedback analysis

## Scaling Considerations

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Enable caching

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple instances
- Shared database/vector store
- Session management (Redis)

### Example Load Balancer Config

```nginx
upstream medical_ai {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://medical_ai;
    }
}
```

## Emergency Contacts

### Technical Issues
- System Admin: [Contact]
- Developer: [Contact]
- Database Admin: [Contact]

### Medical/Legal Issues
- Medical Director: [Contact]
- Legal Counsel: [Contact]
- Compliance Officer: [Contact]

## Compliance Checklist

### HIPAA Compliance (if applicable)
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] Access logging
- [ ] User authentication
- [ ] Regular security audits

### GDPR Compliance (if applicable)
- [ ] Data privacy policy
- [ ] User consent mechanisms
- [ ] Data deletion procedures
- [ ] Data export functionality

## Success Metrics

### Technical Metrics
- Uptime: > 99.5%
- Response time: < 3 seconds
- Error rate: < 1%
- Concurrent users: 50+

### Business Metrics
- User satisfaction: > 4/5
- Query resolution rate: > 90%
- Agent handoff accuracy: > 95%

---

## Final Deployment Approval

**Approved by**: _______________  
**Date**: _______________  
**Deployment Date**: _______________  
**Rollback Plan Tested**: [ ] Yes [ ] No

---

**Remember**: Always test in staging before production deployment!
