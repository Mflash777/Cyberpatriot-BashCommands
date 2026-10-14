#!/bin/bash
# CyberPatriot Quick Wins - Linux Mint 21.3
#
# Usage:   sudo bash linux-mint-wins.sh [--fast]
#          --fast skips the two slowest steps (full system upgrade and installing scanners)
#
# Educational use on authorized CyberPatriot practice images only.
# Read the competition README FIRST: its authorized users and required services
# always override what this script does.
#
# Notes:
#  - Safe to run more than once (config edits are guarded or replaced, not stacked).
#  - Steps 1, 10 and 11 need access to the package repositories. If the image is
#    offline those steps fail and the script keeps going.

export DEBIAN_FRONTEND=noninteractive

FAST=0
[ "$1" = "--fast" ] && FAST=1

echo "=== CyberPatriot - Linux Mint 21.3 Quick Wins ==="

# Must be root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root:  sudo bash linux-mint-wins.sh"
    exit 1
fi

# Under sudo, $HOME can point at /root, so find the real user's Desktop
REAL_USER="${SUDO_USER:-root}"
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
REAL_HOME="${REAL_HOME:-/root}"

LOGDIR="$REAL_HOME/Desktop/CP18_Linux_Logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/linux_mint_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "[$(date)] Starting CyberPatriot Quick Wins Script"

# Keep one pristine backup of a file (never overwrite an existing backup)
backup() {
    if [ -f "$1" ] && [ ! -f "$1.backup" ]; then
        cp -p "$1" "$1.backup"
    fi
}

# 1. UPDATE SYSTEM
echo ""
echo "[1/15] Updating System Packages..."
if [ "$FAST" -eq 1 ]; then
    echo "Skipped (--fast). Run 'apt-get update && apt-get upgrade -y' later."
else
    apt-get update
    apt-get upgrade -y
    echo "System updated"
fi

# 2. ENABLE FIREWALL
echo ""
echo "[2/15] Enabling UFW Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw logging on
ufw --force enable
echo "Firewall enabled and configured"

# 3. DISABLE GUEST ACCOUNT
echo ""
echo "[3/15] Disabling Guest Account..."
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/50-no-guest.conf <<'EOF'
[Seat:*]
allow-guest=false
EOF
# /etc/lightdm/lightdm.conf is read last and wins, so fix it too if it sets guest login
if [ -f /etc/lightdm/lightdm.conf ]; then
    backup /etc/lightdm/lightdm.conf
    sed -i 's/^allow-guest=.*/allow-guest=false/' /etc/lightdm/lightdm.conf
fi
echo "Guest account disabled"

# 4. PASSWORD POLICIES
echo ""
echo "[4/15] Setting Password Policies..."

backup /etc/login.defs
backup /etc/pam.d/common-password
backup /etc/pam.d/common-auth
backup /etc/pam.d/common-account

# Password aging (anchored so comment lines are not touched)
sed -i -E 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs
sed -i -E 's/^PASS_MIN_DAYS.*/PASS_MIN_DAYS   10/' /etc/login.defs
sed -i -E 's/^PASS_WARN_AGE.*/PASS_WARN_AGE   7/'  /etc/login.defs

# Password complexity (pam_pwquality)
apt-get install -y libpam-pwquality
if grep -qE '^password.*pam_pwquality\.so' /etc/pam.d/common-password; then
    if ! grep -E '^password.*pam_pwquality\.so' /etc/pam.d/common-password | grep -q 'minlen='; then
        sed -i -E '/^password.*pam_pwquality\.so/ s/$/ minlen=8 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1/' /etc/pam.d/common-password
    fi
else
    echo "WARNING: pam_pwquality is not in common-password; set complexity manually."
fi

# Password history
sed -i -E '/^password.*pam_unix\.so/ { /remember=/! s/$/ remember=5/ }' /etc/pam.d/common-password

# Account lockout.
# Only touch PAM if the module really exists: a line that names a missing module
# can lock every user out. The auth line goes BEFORE pam_unix so the skip counts
# of the existing lines are unaffected, and the account line resets the counter.
TALLY_SO="$(find /lib /usr/lib -name pam_tally2.so 2>/dev/null | head -n 1)"
if grep -qE 'pam_tally2\.so|pam_faillock\.so' /etc/pam.d/common-auth; then
    echo "Account lockout already configured"
elif [ -n "$TALLY_SO" ]; then
    sed -i '0,/^auth.*pam_unix\.so/s//auth    required                        pam_tally2.so deny=5 unlock_time=1800 onerr=fail\n&/' /etc/pam.d/common-auth
    if ! grep -q 'pam_tally2\.so' /etc/pam.d/common-account; then
        echo 'account required                        pam_tally2.so' >> /etc/pam.d/common-account
    fi
    echo "Account lockout configured (pam_tally2)"
else
    echo "pam_tally2 not found on this image; configure pam_faillock manually."
fi

echo "Password policies configured"
echo "TIP: open a second terminal and confirm 'sudo -k; sudo true' still works before closing this one."

# 5. LOCK ROOT ACCOUNT
echo ""
echo "[5/15] Locking Root Account..."
passwd -l root
echo "Root account locked"

# 6. SET CORRECT PERMISSIONS
echo ""
echo "[6/15] Setting File Permissions..."
chmod 640 /etc/shadow
chmod 644 /etc/passwd
chmod 644 /etc/group
echo "File permissions set"

# 7. DISABLE UNNECESSARY SERVICES (check the README for required services first!)
echo ""
echo "[7/15] Disabling Unnecessary Services..."

SERVICES_TO_DISABLE=(
    "telnet"
    "ftp"
    "vsftpd"
    "apache2"
    "nginx"
    "samba"
    "smbd"
    "nmbd"
    "snmpd"
    "avahi-daemon"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null || systemctl is-enabled --quiet "$service" 2>/dev/null; then
        systemctl stop "$service" 2>/dev/null
        systemctl disable "$service" 2>/dev/null
        echo "Disabled $service"
    fi
done

echo "Services checked and disabled"

# 8. REMOVE UNAUTHORIZED SOFTWARE (check the README for allowed software first!)
echo ""
echo "[8/15] Removing Unauthorized Software..."

PROHIBITED_PACKAGES=(
    "john"
    "hydra"
    "ophcrack"
    "aircrack-ng"
    "wireshark"
    "nmap"
    "netcat"
    "zeitgeist"
    "inetutils-telnet"
    "telnetd"
)

for package in "${PROHIBITED_PACKAGES[@]}"; do
    # Exact match on installed packages (a prefix match would also hit libraries)
    if dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q "install ok installed"; then
        apt-get purge -y "$package"
        echo "Removed $package"
    fi
done

echo "Unauthorized software removal completed"

# 9. FIND MEDIA FILES (listed for review, not deleted)
echo ""
echo "[9/15] Finding Media Files..."
find /home \( -iname '*.mp3' -o -iname '*.mp4' -o -iname '*.avi' -o -iname '*.mkv' \) -type f > "$LOGDIR/media_files.txt" 2>/dev/null
echo "Media files list saved to $LOGDIR/media_files.txt"

# 10. ENABLE AUTOMATIC UPDATES
echo ""
echo "[10/15] Enabling Automatic Updates..."
apt-get install -y unattended-upgrades
# Written directly: 'dpkg-reconfigure unattended-upgrades' opens an interactive
# prompt that would freeze the script.
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
echo "Automatic updates enabled"

# 11. INSTALL SECURITY TOOLS
echo ""
echo "[11/15] Installing Security Tools..."
if [ "$FAST" -eq 1 ]; then
    echo "Skipped (--fast). Run 'apt-get install -y clamav rkhunter chkrootkit' later."
else
    apt-get install -y clamav clamav-daemon rkhunter chkrootkit
    systemctl stop clamav-freshclam 2>/dev/null
    freshclam
    systemctl start clamav-freshclam 2>/dev/null
    echo "Security tools installed"
fi

# 12. CONFIGURE SYSCTL (replaces its own block, so re-running does not duplicate lines)
echo ""
echo "[12/15] Configuring Kernel Parameters..."

backup /etc/sysctl.conf
sed -i '/# BEGIN CP-QUICKWINS/,/# END CP-QUICKWINS/d' /etc/sysctl.conf
cat >> /etc/sysctl.conf <<'EOF'
# BEGIN CP-QUICKWINS
# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 1

# Ignore Broadcast Request
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Enable TCP SYN Cookies
net.ipv4.tcp_syncookies = 1
# END CP-QUICKWINS
EOF

sysctl -p
echo "Kernel parameters configured"

# 13. DISABLE IPV6 (check the README: skip if IPv6 is required)
echo ""
echo "[13/15] Disabling IPv6..."
sed -i '/# BEGIN CP-IPV6/,/# END CP-IPV6/d' /etc/sysctl.conf
cat >> /etc/sysctl.conf <<'EOF'
# BEGIN CP-IPV6
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
# END CP-IPV6
EOF
sysctl -p
echo "IPv6 disabled"

# 14. SECURE SSH (only if the SSH server is installed)
echo ""
echo "[14/15] Securing SSH..."
SSHD=/etc/ssh/sshd_config
if [ -f "$SSHD" ]; then
    backup "$SSHD"
    # sshd uses the FIRST value it finds, so remove old copies and put ours at the top.
    # 'Protocol' is removed: modern OpenSSH only speaks protocol 2 and rejects the option.
    sed -i -E '/^[[:space:]]*#?[[:space:]]*(PermitRootLogin|PermitEmptyPasswords|Protocol)[[:space:]]/d' "$SSHD"
    sed -i '1i PermitRootLogin no\nPermitEmptyPasswords no' "$SSHD"
    # Validate before restarting so a typo can never take SSH down
    if sshd -t 2>/dev/null; then
        systemctl restart sshd 2>/dev/null || systemctl restart ssh 2>/dev/null
        echo "SSH secured"
    else
        echo "sshd_config failed validation; restoring backup"
        cp -p "$SSHD.backup" "$SSHD"
    fi
else
    echo "SSH not installed"
fi

# 15. USER PASSWORDS (manual on purpose: the README decides who is authorized)
echo ""
echo "[15/15] User Password Management..."
echo "Please set passwords for all users manually using: passwd <username>"
echo "Authorized users should be listed in the README"

# Give the log folder back to the real user
chown -R "$REAL_USER:" "$LOGDIR" 2>/dev/null

echo ""
echo "=== Quick Wins Script Completed ==="
echo "Log file saved to: $LOGFILE"
echo "Check the scoring report for points!"
echo "Next steps:"
echo "1. Read the README carefully"
echo "2. Answer forensics questions"
echo "3. Review unauthorized users/software"
echo "4. Check for prohibited files (see media_files.txt)"
echo "5. Review all services and configurations"
