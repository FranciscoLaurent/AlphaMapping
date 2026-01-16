# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT

- Open a public GitHub issue
- Disclose the vulnerability publicly before it's fixed

### Do

1. **Email** the maintainers directly (preferred)
2. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Release**: Depends on severity (Critical: ASAP, High: 2 weeks, Medium/Low: Next release)

## Security Best Practices

When deploying AlphaMapping:

### Environment Variables

- Never commit `.env` files to version control
- Use strong, unique API keys
- Rotate credentials regularly

### Network Security

- Use HTTPS in production
- Configure firewall rules appropriately
- Limit API access to trusted networks if possible

### Docker Deployment

- Keep base images updated
- Run containers as non-root user
- Use Docker secrets for sensitive data

## Known Limitations

1. **SQLite** - Default database is SQLite, suitable for development. Consider PostgreSQL for production.

2. **Authentication** - Current version does not include user authentication. Deploy behind a VPN or add authentication layer if needed.

3. **Rate Limiting** - No built-in rate limiting. Consider using a reverse proxy (nginx, Traefik) with rate limiting for public deployments.

## Security Updates

Security updates will be announced through:
- GitHub Releases
- CHANGELOG.md

---

Thank you for helping keep AlphaMapping secure!
