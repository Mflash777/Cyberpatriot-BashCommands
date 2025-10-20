#!/bin/bash
# CyberPatriot 18 - Linux Mint 21.3 Quick Wins Script
# Run with sudo: sudo bash linux_quickwins.sh
# Created for GHP Computer Science Portfolio

echo "=== CyberPatriot 18 - Linux Mint 21.3 Quick Wins ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo bash script.sh)"
    exit 1
fi

# Create log directory
LOGDIR="$HOME/Desktop/CP18_Linux_Logs"
mkdir -p "$LOGDIR"
LOGFILE="$LOGDIR/linux_mint_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "[$(date)] Starting CyberPatriot Quick Wins Script"

# 1. UPDATE SYSTEM
echo ""
echo "[1/15] Updating System Packages..."
apt update
apt upgrade -y
echo "System updated"

# 2. ENABLE FIREWALL
echo ""
echo "[2/15] Enabling UFW Firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw logging on
echo "Firewall enabled and configured"

# 3. DISABLE GUEST ACCOUNT
echo ""
echo "[3/15] Disabling Guest Account..."
if [ -f /etc/lightdm/lightdm.conf ]; then
    echo "allow-guest=false" >> /etc/lightdm/lightdm.conf
else
    mkdir -p /etc/lightdm/lightdm.conf.d
    echo "[Seat:*]" > /etc/lightdm/lightdm.conf.d/50-no-guest.conf
    echo "allow-guest=false" >> /etc/lightdm/lightdm.conf.d/50-no-guest.conf
fi
echo "Guest account disabled"

# 4. PASSWORD POLICIES
echo ""
echo "[4/15] Setting Password Policies..."

# Backup original files
cp /etc/login.defs /etc/login.defs.backup
cp /etc/pam.d/common-password /etc/pam.d/common-password.backup
cp /etc/pam.d/common-auth /etc/pam.d/common-auth.backup

# Set password aging in login.defs
sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs
sed -i 's/PASS_MIN_DAYS.*/PASS_MIN_DAYS   10/' /etc/login.defs
sed -i 's/PASS_WARN_AGE.*/PASS_WARN_AGE   7/' /etc/login.defs
sed -i 's/PASS_MIN_LEN.*/PASS_MIN_LEN    8/' /etc/login.defs

# Password complexity with PAM
apt install -y libpam-pwquality
sed -i '/pam_pwquality.so/ s/$/ minlen=8 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1/' /etc/pam.d/common-password

# Password history
sed -i '/pam_unix.so/ s/$/ remember=5/' /etc/pam.d/common-password

# Account lockout
echo "auth required pam_tally2.so deny=5 unlock_time=1800 onerr=fail" >> /etc/pam.d/common-auth

echo "Password policies configured"

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

# 7. DISABLE UNNECESSARY SERVICES
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
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        systemctl stop "$service"
        systemctl disable "$service"
        echo "Disabled $service"
    fi
done

echo "Services checked and disabled"

# 8. REMOVE UNAUTHORIZED SOFTWARE
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
    "nc"
    "zeitgeist"
    "nginx"
    "inetutils-telnet"
    "telnetd"
)

for package in "${PROHIBITED_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $package"; then
        apt purge -y "$package"
        echo "Removed $package"
    fi
done

echo "Unauthorized software removal completed"

# 9. REMOVE MEDIA FILES
echo ""
echo "[9/15] Finding Media Files..."
find /home -name "*.mp3" -o -name "*.mp4" -o -name "*.avi" -o -name "*.mkv" > "$LOGDIR/media_files.txt"
echo "Media files list saved to $LOGDIR/media_files.txt"

# 10. ENABLE AUTOMATIC UPDATES
echo ""
echo "[10/15] Enabling Automatic Updates..."
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
echo "Automatic updates enabled"

# 11. INSTALL SECURITY TOOLS
echo ""
echo "[11/15] Installing Security Tools..."
apt install -y clamav clamav-daemon rkhunter chkrootkit
freshclam
echo "Security tools installed"

# 12. CONFIGURE SYSCTL
echo ""
echo "[12/15] Configuring Kernel Parameters..."

cat >> /etc/sysctl.conf << EOF
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
EOF

sysctl -p
echo "Kernel parameters configured"

# 13. DISABLE IPV6 (if not required)
echo ""
echo "[13/15] Disabling IPv6..."
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p
echo "IPv6 disabled"

# 14. SECURE SSH (if needed)
echo ""
echo "[14/15] Securing SSH..."
if [ -f /etc/ssh/sshd_config ]; then
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PermitEmptyPasswords.*/PermitEmptyPasswords no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/#Protocol.*/Protocol 2/' /etc/ssh/sshd_config
    systemctl restart sshd 2>/dev/null || systemctl restart ssh 2>/dev/null
    echo "SSH secured"
else
    echo "SSH not installed"
fi

# 15. SET USER PASSWORDS
echo ""
echo "[15/15] User Password Management..."
echo "Please set passwords for all users manually using: passwd <username>"
echo "Authorized users should be listed in the README"

echo ""
echo "=== Quick Wins Script Completed ==="
echo "Log file saved to: $LOGFILE"
echo "Check the scoring report for points!"
echo "Next steps:"
echo "1. Read the README carefully"
echo "2. Answer forensics questions"
echo "3. Review unauthorized users/software"
echo "4. Check for prohibited files"
echo "5. Review all services and configurations"
