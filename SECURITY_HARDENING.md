# Docker Deployment Security Hardening Guide

## Critical Changes Applied

### 1. **Secrets Management**

- ✅ Removed hardcoded default credentials
- ✅ All secrets now required via `.env` file (not committed to git)
- ✅ Environment variables use `${VAR}` with no defaults, forcing explicit configuration

**Action Required:**

```bash
# Copy the example file
cp .env.example .env

# Generate strong passwords
openssl rand -base64 32  # Use for NEO4J_PASSWORD
openssl rand -base64 32  # Use for GRAFANA_ADMIN_PASSWORD

# Edit .env and replace placeholder values
nano .env

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

### 2. **Disabled Anonymous Access**

- ✅ Grafana anonymous access disabled: `GF_AUTH_ANONYMOUS_ENABLED=false`
- ✅ User sign-up disabled: `GF_USERS_ALLOW_SIGN_UP=false`
- ✅ All services now require authentication

### 3. **Enhanced Security Headers**

- ✅ HTTP-only cookies: `GF_SECURITY_COOKIE_HTTPONLY=true`
- ✅ SameSite cookies: `GF_SECURITY_COOKIE_SAMESITE=Lax` (local HTTP stack)
- ✅ Secure cookies disabled for local HTTP (`GF_SECURITY_COOKIE_SECURE=false`); enable only behind HTTPS
- ✅ Initial admin password-change wall disabled for local defaults (`GF_SECURITY_DISABLE_INITIAL_ADMIN_PASSWORD_CHANGE=true`)
- ✅ No new privileges flag: `security_opt: no-new-privileges:true`

### 4. **Resource Limits**

- ✅ All containers have CPU and memory limits to prevent resource exhaustion DoS
- ✅ Prometheus: 0.5 CPU / 512MB memory max
- ✅ Grafana: 0.5 CPU / 512MB memory max
- ✅ Skills UI: 0.5 CPU / 256MB memory max
- ✅ Skills API: 2 CPU / 1GB memory max
- ✅ Neo4j: 1 CPU / 2GB memory max
- ✅ Skills Loader: 2 CPU / 1GB memory max

### 5. **Read-Only Filesystems**

- ✅ All containers use `read_only: true` where possible
- ✅ Temporary directories (`/tmp`, `/run`) mounted as tmpfs
- ✅ Reduces attack surface from filesystem modifications
- ✅ Configuration files mounted read-only (`:ro`)

### 6. **Improved Logging**

- ✅ JSON file logging driver configured
- ✅ Log rotation: 10MB max per file, 3 file retention
- ✅ Prevents disk space exhaustion from logs

### 7. **Health Checks**

- ✅ Neo4j: HTTP health check every 5s
- ✅ Skills API: Added health check endpoint requirement
- ✅ Auto-restart on failure: `restart: unless-stopped`

### 8. **Volume Management**

- ✅ Named volumes with explicit bind mount locations
- ✅ Data persisted in `./data/` directory (update paths as needed)
- ✅ Structured volume layout for easier backup/recovery

### 9. **Network Security**

- ✅ All services bound to `127.0.0.1` (localhost only)
- ✅ Services communicate via internal Docker network
- ✅ No exposure to external networks by default

### 10. **Additional Hardening**

- ✅ Neo4j security settings: disabled unrestricted procedures
- ✅ Grafana log level set to "warn" (reduces log noise)
- ✅ TLS configuration for Neo4j bolt connections
- ✅ Basic auth enabled in Grafana

## Ongoing Security Practices

### Vulnerability Scanning

```bash
# Scan images with Docker Scout
docker scout cves --multi-platform coding-agent-skill-library-skills-api
docker scout cves --multi-platform neo4j:5.26-community
docker scout cves --multi-platform grafana/grafana:11.4.0
docker scout cves --multi-platform prom/prometheus:v3.0.1
```

### Secrets Rotation

- Rotate `NEO4J_PASSWORD` every 90 days
- Rotate `GRAFANA_ADMIN_PASSWORD` every 90 days
- Use a secrets management tool for production (e.g., HashiCorp Vault, AWS Secrets Manager)

### Network Isolation (Production)

```yaml
# For production, implement network segmentation:
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
  database:
    driver: bridge

services:
  skills-ui:
    networks:
      - frontend
  skills-api:
    networks:
      - frontend
      - backend
  neo4j:
    networks:
      - backend
      - database
```

### Firewall Rules

```bash
# Example UFW rules (adjust as needed)
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 3000  # Grafana
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 9090  # Prometheus
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 8000  # Skills API
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 5173  # Skills UI
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 7474  # Neo4j HTTP
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 7687  # Neo4j Bolt
```

### Image Build Security

```bash
# Always pull images with digest verification
docker pull neo4j:5.26-community
docker inspect neo4j:5.26-community --format='{{index .RepoDigests 0}}'

# Pin images to specific digests in production
# Example: neo4j:5.26-community@sha256:aca21b24d5ef07d26bac6fcdf2cd937150a0df2b2f826332e249c08d583c8d2b
```

### Backup Strategy

```bash
# Backup Neo4j data
docker compose exec neo4j neo4j-admin dump --database=neo4j --to=/data/backup.dump

# Backup volumes
tar -czf backups/neo4j-$(date +%Y%m%d).tar.gz data/neo4j/
tar -czf backups/grafana-$(date +%Y%m%d).tar.gz data/grafana/
tar -czf backups/prometheus-$(date +%Y%m%d).tar.gz data/prometheus/
```

### Monitoring & Alerting

- Monitor resource usage against limits: `docker stats`
- Watch for privilege escalation attempts in logs: `docker compose logs`
- Set up Prometheus alerts for service downtime
- Create Grafana dashboards for security metrics

### Compliance Checklist

- [ ] `.env` file excluded from version control
- [ ] Strong passwords (32+ characters) generated and set
- [ ] Secrets stored in encrypted vault for production
- [ ] Image vulnerability scans scheduled (weekly minimum)
- [ ] Access logs monitored for suspicious activity
- [ ] Disaster recovery/backup plan documented
- [ ] Security incidents response plan in place
- [ ] Regular security audits scheduled (quarterly minimum)

## Deployment Verification

After applying changes:

```bash
# Verify no hardcoded secrets remain
grep -r "testpassword" . --exclude-dir=.git --exclude-dir=.venv
grep -r "admin" docker-compose.yml | grep -v "\${" | grep -v "#"

# Verify .env is properly sourced
docker compose config | grep NEO4J_PASSWORD

# Test all health checks
docker compose ps  # Should show "healthy" status

# Verify resource limits are applied
docker inspect coding-agent-skill-library-neo4j-1 | grep -A 20 "MemoryLimit"

# Check read-only filesystems
docker inspect coding-agent-skill-library-skills-api-1 | grep -i readonly
```

## References

- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Container Security Top 10](https://owasp.org/www-project-container-security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [NIST Container Security Guidelines](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
