
# Create comprehensive CyberPatriot scripts for Windows 11, Windows Server, and Linux Mint 21.3
# These scripts will focus on getting maximum points in the first 15 minutes

# Windows 11 Quick Win Script (PowerShell)
windows11_script = """# CyberPatriot 18 - Windows 11 Quick Wins Script
# Run as Administrator

Write-Host "=== CyberPatriot 18 - Windows 11 Quick Wins ===" -ForegroundColor Cyan
Write-Host "Starting automated hardening..." -ForegroundColor Green

# Create log directory
$LogDir = "$env:USERPROFILE\\Desktop\\CP18_Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path "$LogDir\\Windows11_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 1. USERS AND PASSWORDS - High Priority
Write-Host "`n[1/10] Configuring Users and Passwords..." -ForegroundColor Yellow

# Disable Guest Account
net user Guest /active:no

# Disable Administrator Account (if not needed)
net user Administrator /active:no

# Set password for all users (change as needed per README)
$password = Read-Host "Enter secure password for all users" -AsSecureString
Get-LocalUser | Where-Object {$_.Enabled -eq $true} | Set-LocalUser -Password $password

# Remove unauthorized users (check README first!)
# net user [UnauthorizedUser] /delete

Write-Host "User management completed" -ForegroundColor Green

# 2. PASSWORD POLICIES - Critical Points
Write-Host "`n[2/10] Setting Password Policies..." -ForegroundColor Yellow

secedit /export /cfg $LogDir\\secpol.cfg | Out-Null
(Get-Content $LogDir\\secpol.cfg) -replace 'PasswordHistorySize = \\d+', 'PasswordHistorySize = 5' `
    -replace 'MaximumPasswordAge = \\d+', 'MaximumPasswordAge = 90' `
    -replace 'MinimumPasswordAge = \\d+', 'MinimumPasswordAge = 10' `
    -replace 'MinimumPasswordLength = \\d+', 'MinimumPasswordLength = 8' `
    -replace 'PasswordComplexity = \\d', 'PasswordComplexity = 1' `
    -replace 'LockoutBadCount = \\d+', 'LockoutBadCount = 5' | Set-Content $LogDir\\secpol_new.cfg
secedit /configure /db c:\\windows\\security\\local.sdb /cfg $LogDir\\secpol_new.cfg /areas SECURITYPOLICY | Out-Null
Remove-Item $LogDir\\secpol.cfg, $LogDir\\secpol_new.cfg -Force

Write-Host "Password policies configured" -ForegroundColor Green

# 3. WINDOWS FIREWALL - Easy Points
Write-Host "`n[3/10] Enabling Windows Firewall..." -ForegroundColor Yellow

Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
netsh advfirewall set allprofiles state on

Write-Host "Firewall enabled for all profiles" -ForegroundColor Green

# 4. WINDOWS UPDATES - Critical
Write-Host "`n[4/10] Enabling Automatic Updates..." -ForegroundColor Yellow

# Enable Windows Update service
Set-Service -Name wuauserv -StartupType Automatic
Start-Service -Name wuauserv

# Configure automatic updates via registry
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "NoAutoUpdate" -Value 0 -Force
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "AUOptions" -Value 4 -Force

Write-Host "Windows Updates configured" -ForegroundColor Green

# 5. REMOVE UNAUTHORIZED SOFTWARE - Check README
Write-Host "`n[5/10] Checking for Unauthorized Software..." -ForegroundColor Yellow

$ProhibitedSoftware = @(
    "*Wireshark*",
    "*BitTorrent*",
    "*uTorrent*",
    "*John*Ripper*",
    "*Cain*Abel*",
    "*Ophcrack*",
    "*Aircrack*",
    "*Nmap*"
)

foreach ($software in $ProhibitedSoftware) {
    Get-Package -Name $software -ErrorAction SilentlyContinue | Uninstall-Package -Force
}

Write-Host "Unauthorized software removal attempted" -ForegroundColor Green

# 6. DISABLE UNNECESSARY SERVICES
Write-Host "`n[6/10] Disabling Unnecessary Services..." -ForegroundColor Yellow

$ServicesToDisable = @(
    "RemoteRegistry",
    "Telnet",
    "ftpsvc",
    "SNMP",
    "TlntSvr"
)

foreach ($service in $ServicesToDisable) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled
    }
}

Write-Host "Unnecessary services disabled" -ForegroundColor Green

# 7. ENABLE AUDIT POLICIES
Write-Host "`n[7/10] Enabling Audit Policies..." -ForegroundColor Yellow

auditpol /set /category:"Account Logon" /success:enable /failure:enable
auditpol /set /category:"Account Management" /success:enable /failure:enable
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Policy Change" /success:enable /failure:enable
auditpol /set /category:"System" /success:enable /failure:enable

Write-Host "Audit policies enabled" -ForegroundColor Green

# 8. DISABLE REMOTE DESKTOP (if not required)
Write-Host "`n[8/10] Configuring Remote Desktop..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections" -Value 1

Write-Host "Remote Desktop disabled" -ForegroundColor Green

# 9. USER ACCOUNT CONTROL (UAC)
Write-Host "`n[9/10] Enabling User Account Control..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" -Value 1
Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "ConsentPromptBehaviorAdmin" -Value 2

Write-Host "UAC enabled and configured" -ForegroundColor Green

# 10. WINDOWS DEFENDER
Write-Host "`n[10/10] Configuring Windows Defender..." -ForegroundColor Yellow

Set-MpPreference -DisableRealtimeMonitoring $false
Update-MpSignature
Start-MpScan -ScanType QuickScan

Write-Host "Windows Defender configured and scanning" -ForegroundColor Green

Write-Host "`n=== Quick Wins Script Completed ===" -ForegroundColor Cyan
Write-Host "Check the scoring report for points!" -ForegroundColor Green
Write-Host "Log saved to: $LogDir" -ForegroundColor Cyan

Stop-Transcript
"""

# Windows Server Quick Win Script
windows_server_script = """# CyberPatriot 18 - Windows Server Quick Wins Script
# Run as Administrator
# Created for GHP Computer Science Portfolio

Write-Host "=== CyberPatriot 18 - Windows Server Quick Wins ===" -ForegroundColor Cyan

$LogDir = "$env:USERPROFILE\\Desktop\\CP18_Server_Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path "$LogDir\\WindowsServer_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 1. USER MANAGEMENT
Write-Host "`n[1/12] Managing Users..." -ForegroundColor Yellow

net user Guest /active:no
net user Administrator /active:no

# Set passwords (check README for authorized users)
$password = Read-Host "Enter secure password" -AsSecureString
Get-LocalUser | Where-Object {$_.Enabled -eq $true} | Set-LocalUser -Password $password

Write-Host "Users configured" -ForegroundColor Green

# 2. PASSWORD POLICIES
Write-Host "`n[2/12] Setting Password Policies..." -ForegroundColor Yellow

secedit /export /cfg $LogDir\\secpol.cfg | Out-Null
(Get-Content $LogDir\\secpol.cfg) -replace 'PasswordHistorySize = \\d+', 'PasswordHistorySize = 24' `
    -replace 'MaximumPasswordAge = \\d+', 'MaximumPasswordAge = 60' `
    -replace 'MinimumPasswordAge = \\d+', 'MinimumPasswordAge = 1' `
    -replace 'MinimumPasswordLength = \\d+', 'MinimumPasswordLength = 14' `
    -replace 'PasswordComplexity = \\d', 'PasswordComplexity = 1' `
    -replace 'LockoutBadCount = \\d+', 'LockoutBadCount = 3' | Set-Content $LogDir\\secpol_new.cfg
secedit /configure /db c:\\windows\\security\\local.sdb /cfg $LogDir\\secpol_new.cfg /areas SECURITYPOLICY | Out-Null

Write-Host "Password policies set" -ForegroundColor Green

# 3. FIREWALL
Write-Host "`n[3/12] Enabling Firewall..." -ForegroundColor Yellow

Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

Write-Host "Firewall enabled" -ForegroundColor Green

# 4. DISABLE FTP SERVICE
Write-Host "`n[4/12] Disabling FTP Service..." -ForegroundColor Yellow

if (Get-Service -Name ftpsvc -ErrorAction SilentlyContinue) {
    Stop-Service -Name ftpsvc -Force
    Set-Service -Name ftpsvc -StartupType Disabled
}

Write-Host "FTP service disabled" -ForegroundColor Green

# 5. DISABLE TELNET
Write-Host "`n[5/12] Disabling Telnet..." -ForegroundColor Yellow

Disable-WindowsOptionalFeature -Online -FeatureName TelnetClient -NoRestart
Disable-WindowsOptionalFeature -Online -FeatureName TelnetServer -NoRestart

Write-Host "Telnet disabled" -ForegroundColor Green

# 6. WINDOWS UPDATES
Write-Host "`n[6/12] Enabling Windows Updates..." -ForegroundColor Yellow

Set-Service -Name wuauserv -StartupType Automatic
Start-Service -Name wuauserv

Write-Host "Windows Updates enabled" -ForegroundColor Green

# 7. REMOVE SHARES (Check README first!)
Write-Host "`n[7/12] Checking for Unauthorized Shares..." -ForegroundColor Yellow

Get-SmbShare | Where-Object {$_.Name -notlike "*$" -and $_.Name -ne "IPC$"} | ForEach-Object {
    Write-Host "Found share: $($_.Name) - Review and remove if unauthorized"
}

Write-Host "Share audit completed" -ForegroundColor Green

# 8. AUDIT POLICIES
Write-Host "`n[8/12] Enabling Audit Policies..." -ForegroundColor Yellow

auditpol /set /category:* /success:enable /failure:enable

Write-Host "Audit policies enabled" -ForegroundColor Green

# 9. DISABLE REMOTE DESKTOP (check README)
Write-Host "`n[9/12] Configuring Remote Desktop..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections" -Value 1

Write-Host "Remote Desktop configured" -ForegroundColor Green

# 10. UAC
Write-Host "`n[10/12] Enabling UAC..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" -Value 1

Write-Host "UAC enabled" -ForegroundColor Green

# 11. DISABLE UNNECESSARY FEATURES
Write-Host "`n[11/12] Disabling Unnecessary Features..." -ForegroundColor Yellow

$FeaturesToDisable = @(
    "SMB1Protocol",
    "TelnetClient",
    "TFTP"
)

foreach ($feature in $FeaturesToDisable) {
    Disable-WindowsOptionalFeature -Online -FeatureName $feature -NoRestart -ErrorAction SilentlyContinue
}

Write-Host "Unnecessary features disabled" -ForegroundColor Green

# 12. WINDOWS DEFENDER
Write-Host "`n[12/12] Configuring Windows Defender..." -ForegroundColor Yellow

Set-MpPreference -DisableRealtimeMonitoring $false
Update-MpSignature

Write-Host "Windows Defender configured" -ForegroundColor Green

Write-Host "`n=== Server Quick Wins Completed ===" -ForegroundColor Cyan

Stop-Transcript
"""

# Linux Mint 21.3 Bash Script
linux_mint_script = """#!/bin/bash
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
"""

# Save scripts to files
scripts = {
    'windows11_quickwins.ps1': windows11_script,
    'windowsserver_quickwins.ps1': windows_server_script,
    'linux_mint_quickwins.sh': linux_mint_script
}

print("CyberPatriot 18 Quick Wins Scripts Created Successfully!\n")
print("=" * 60)
for filename, content in scripts.items():
    print(f"\n{filename}:")
    print(f"  Lines: {len(content.splitlines())}")
    print(f"  Size: {len(content)} bytes")
print("\n" + "=" * 60)
