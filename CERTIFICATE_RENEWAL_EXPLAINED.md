# Certificate Renewal Configuration Explained

## 📋 Overview

The Let's Encrypt renewal configuration file at `/etc/letsencrypt/renewal/3netra.in.conf` tells Certbot how to automatically renew your SSL certificates when they're about to expire.

---

## 📄 Configuration File Breakdown

### Certificate Paths

```
cert = /etc/letsencrypt/live/3netra.in/cert.pem
privkey = /etc/letsencrypt/live/3netra.in/privkey.pem
chain = /etc/letsencrypt/live/3netra.in/chain.pem
fullchain = /etc/letsencrypt/live/3netra.in/fullchain.pem
```

**What it means:**
- These point to the actual certificate files
- Certbot expects these to be **symlinks** pointing to files in `/etc/letsencrypt/archive/3netra.in/`
- When certificates are renewed, Certbot creates new files (e.g., `cert2.pem`, `cert3.pem`) and updates these symlinks
- ✅ **Status**: Symlinks are now correctly configured

### Archive Directory

```
archive_dir = /etc/letsencrypt/archive/3netra.in
```

**What it means:**
- This is where Certbot stores all versions of your certificates (cert1.pem, cert2.pem, etc.)
- Old certificates are kept here for rollback purposes
- The `live/` directory symlinks always point to the latest version

### Renewal Parameters

```
[renewalparams]
account = 00675b512db2ebca8c536be56ec8dd83
authenticator = webroot
installer = None
server = https://acme-v02.api.letsencrypt.org/directory
webroot_path = /var/www/certbot, /var/www/certbot
```

**What each means:**
- **`account`**: Your Let's Encrypt account ID (links to your registered account)
- **`authenticator = webroot`**: Uses HTTP validation (places files in webroot for Let's Encrypt to verify)
- **`installer = None`**: Certbot won't automatically modify nginx config (we handle it manually)
- **`server`**: Let's Encrypt API endpoint (production)
- **`webroot_path`**: Directory where ACME challenge files are placed (`/var/www/certbot`)
  - ⚠️ **Important**: This directory must be accessible via HTTP (not HTTPS) for validation
  - ✅ **Status**: Mounted in docker-compose.yml at `/var/www/certbot`

### Webroot Map

```
[[webroot_map]]
3netra.in = /var/www/certbot
www.3netra.in = /var/www/certbot
```

**What it means:**
- Maps each domain to its webroot path for ACME challenge validation
- Both `3netra.in` and `www.3netra.in` use the same webroot
- When Let's Encrypt validates, it accesses:
  - `http://3netra.in/.well-known/acme-challenge/[token]`
  - `http://www.3netra.in/.well-known/acme-challenge/[token]`

### Post-Renewal Hook

```
post_hook = /root/Face-Liveness-Detection-Anti-Spoofing-Web-App/reload-nginx.sh
```

**What it means:**
- After a successful renewal, Certbot runs this script
- The script reloads the nginx container to pick up new certificates
- ✅ **Status**: Script exists and is executable at `/root/Face-Liveness-Detection-Anti-Spoofing-Web-App/reload-nginx.sh`

### Renew Before Expiry (Commented Out)

```
# renew_before_expiry = 30 days
```

**What it means:**
- This setting controls when to start renewing certificates
- **Default**: 30 days before expiry (if not specified)
- Since it's commented out, Certbot uses the default (30 days)
- Let's Encrypt certificates are valid for 90 days
- Renewal happens automatically 30 days before expiry (at ~60 days old)

**Current certificate status:**
- **Expiry Date**: 2025-12-26
- **Days Remaining**: ~41 days
- **Next Renewal**: Will attempt around 2025-11-26 (30 days before expiry)

---

## 🔄 How Auto-Renewal Works

1. **Systemd Timer** (or cron job) runs `certbot renew` periodically (typically twice daily)
2. **Certbot checks** if certificates expire within 30 days
3. **If renewal needed:**
   - Places ACME challenge files in `/var/www/certbot/.well-known/acme-challenge/`
   - Let's Encrypt validates by accessing `http://3netra.in/.well-known/acme-challenge/[token]`
   - Downloads new certificates to `/etc/letsencrypt/archive/3netra.in/cert[N].pem`
   - Updates symlinks in `/etc/letsencrypt/live/3netra.in/`
   - Runs `post_hook` script to reload nginx
4. **Nginx reloads** and picks up new certificates (zero downtime)

---

## ✅ Verification

### Check Certificate Status

```bash
sudo certbot certificates
```

### Test Renewal (Dry Run)

```bash
sudo certbot renew --dry-run
```

This simulates renewal without actually renewing certificates.

### Check Renewal Schedule

```bash
# Check systemd timer (if using systemd)
sudo systemctl status certbot.timer

# Check timer schedule
sudo systemctl list-timers | grep certbot
```

---

## ⚠️ Important Notes

1. **ACME Challenge Access**: The `.well-known/acme-challenge/` path must be accessible via **HTTP** (port 80), not HTTPS. Your nginx config already handles this correctly.

2. **Symlinks Required**: The files in `/etc/letsencrypt/live/3netra.in/` must be symlinks, not regular files. ✅ Fixed.

3. **Post-Hook Script**: Must be executable and able to reload nginx. ✅ Configured.

4. **Auto-Renewal**: Certbot typically runs via systemd timer or cron. Check if it's enabled:
   ```bash
   sudo systemctl enable certbot.timer
   sudo systemctl start certbot.timer
   ```

---

## 🔧 Troubleshooting

### If Renewal Fails

1. **Check ACME challenge access:**
   ```bash
   curl http://3netra.in/.well-known/acme-challenge/test
   ```
   Should return 404 (file not found) or 403 (forbidden), NOT 301 redirect.

2. **Check webroot path:**
   ```bash
   sudo ls -la /var/www/certbot/.well-known/acme-challenge/
   ```

3. **Check nginx logs:**
   ```bash
   docker-compose logs nginx | grep acme
   ```

4. **Test renewal manually:**
   ```bash
   sudo certbot renew --dry-run -v
   ```

---

## 📚 References

- [Certbot Renewal Configuration](https://eff-certbot.readthedocs.io/en/stable/using.html#renewal)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

