# Security Checklist

## Pre-Deployment Security Review

### Secrets Management
- [ ] No API keys committed to repository
- [ ] No passwords in .env files committed to git
- [ ] Database credentials use environment variables
- [ ] LLM API key uses environment variable with placeholder comment
- [ ] Production uses secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)

### Database Security
- [ ] PostgreSQL uses strong password
- [ ] Database connection uses SSL/TLS in production
- [ ] Database user has minimal required permissions
- [ ] pg_trgm extension properly sandboxed
- [ ] Regular backups configured
- [ ] Backup encryption enabled

### API Security
- [ ] CORS properly configured (not using `*` in production)
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using ORM parameterized queries)
- [ ] Rate limiting implemented (consider adding nginx rate limiting)
- [ ] Authentication implemented (if required)
- [ ] HTTPS/TLS enabled in production

### Application Security
- [ ] Dependencies up to date (run `pip audit` and `npm audit`)
- [ ] No debug mode in production
- [ ] Logging doesn't expose sensitive data
- [ ] Error messages don't leak system information
- [ ] File upload validation (if implemented)
- [ ] XSS protection in frontend

### Docker Security
- [ ] Using specific image versions (not `latest`)
- [ ] Container runs as non-root user (consider adding)
- [ ] Secrets not in Dockerfile
- [ ] .dockerignore excludes sensitive files
- [ ] Minimal base images used
- [ ] Regular security updates applied

### LLM Security
- [ ] LLM API key stored securely
- [ ] LLM prompts prevent injection attacks
- [ ] LLM never returns calorie calculations (only ingredient suggestions)
- [ ] Rate limiting on LLM calls
- [ ] Input sanitization before LLM calls

### Data Privacy
- [ ] User data minimization
- [ ] Clear data retention policy
- [ ] GDPR compliance (if applicable)
- [ ] Privacy policy published
- [ ] User consent for data collection

### Network Security
- [ ] Production uses HTTPS only
- [ ] Database not exposed to public internet
- [ ] Redis not exposed to public internet
- [ ] Firewall rules properly configured
- [ ] VPC/network segmentation in place

### Monitoring & Incident Response
- [ ] Logging configured and centralized
- [ ] Security alerts configured
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Vulnerability disclosure process defined

## Running Security Checks

### Python Dependencies
```bash
cd backend
pip install pip-audit
pip-audit
```

### Node Dependencies
```bash
cd frontend
npm audit
npm audit fix  # Fix automatically if possible
```

### Docker Image Scanning
```bash
# Scan backend image
docker scan calories-backend:latest

# Scan frontend image
docker scan calories-frontend:latest
```

### Static Code Analysis
```bash
# Python: bandit
cd backend
pip install bandit
bandit -r . -ll

# Python: safety
pip install safety
safety check
```

### Database Security Check
```sql
-- Check PostgreSQL configuration
SHOW ssl;
SHOW password_encryption;
SELECT * FROM pg_roles WHERE rolname = 'calories';
```

## Common Vulnerabilities to Check

### SQL Injection
- ✅ Using SQLAlchemy ORM with parameterized queries
- ✅ No raw SQL with user input concatenation

### Cross-Site Scripting (XSS)
- ✅ Angular automatically escapes output
- ⚠️ Review any use of `innerHTML` or `bypassSecurityTrust`

### Cross-Site Request Forgery (CSRF)
- ⚠️ Consider adding CSRF tokens for state-changing operations
- ✅ CORS configured

### Insecure Dependencies
- Regular updates needed
- Monitor security advisories

### Sensitive Data Exposure
- ✅ No secrets in code
- ✅ Environment variables for configuration
- ⚠️ Review logs for sensitive data leaks

### Broken Authentication
- Not implemented yet (consider adding for production)
- Use established libraries (OAuth, JWT)

### Security Misconfiguration
- ✅ Separate dev/prod configurations
- ⚠️ Review CORS, CSP headers
- ⚠️ Disable debug mode in production

## Recommended Security Headers

Add these to nginx/production proxy:

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Incident Response

If a security issue is discovered:

1. **Assess Impact**: Determine scope and severity
2. **Contain**: Isolate affected systems
3. **Notify**: Inform stakeholders
4. **Fix**: Patch vulnerability
5. **Verify**: Test fix thoroughly
6. **Deploy**: Roll out fix
7. **Monitor**: Watch for further issues
8. **Document**: Record incident details
9. **Review**: Conduct post-mortem
10. **Improve**: Update processes

## Regular Security Maintenance

### Weekly
- [ ] Review logs for suspicious activity
- [ ] Check for dependency updates

### Monthly
- [ ] Run security scans
- [ ] Review access logs
- [ ] Update dependencies
- [ ] Review OWASP Top 10

### Quarterly
- [ ] Full security audit
- [ ] Penetration testing
- [ ] Update incident response plan
- [ ] Security training for team

### Annually
- [ ] Third-party security assessment
- [ ] Compliance review
- [ ] Disaster recovery testing
- [ ] Update security policies

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Angular Security Guide](https://angular.io/guide/security)

## Contact

For security issues, please email: [security@yourdomain.com]

**Do not** open public issues for security vulnerabilities.
