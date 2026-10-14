# Create CyberPatriot Quick Wins scripts for Windows 11, Windows Server 2019, and Linux Mint 21.3
# Run:  python3 make_scripts.py       (creates the files in ./cyberpatriot-quickwins)
#
# Raw strings (r"""...""") are used so backslashes in PowerShell paths and sed
# patterns are written exactly as they will appear in the generated files.

from pathlib import Path

OUT_DIR = Path("cyberpatriot-quickwins")

# ---------------------------------------------------------------------------
# Windows 11 (PowerShell)
# ---------------------------------------------------------------------------
windows11_script = r"""#Requires -RunAsAdministrator
# CyberPatriot Quick Wins - Windows 11
#
# Usage (elevated PowerShell):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\windows11-wins.ps1
#
# Educational use on authorized CyberPatriot practice images only.
# Read the competition README FIRST: its authorized users and required services
# always override what this script does.

Write-Host "=== CyberPatriot - Windows 11 Quick Wins ===" -ForegroundColor Cyan
Write-Host "Starting automated hardening..." -ForegroundColor Green

# Create log directory
$LogDir = Join-Path $env:USERPROFILE 'Desktop\CP18_Logs'
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path (Join-Path $LogDir ("Windows11_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss')))

# 1. USERS AND PASSWORDS - High Priority
Write-Host "`n[1/10] Configuring Users and Passwords..." -ForegroundColor Yellow

# Disable Guest Account
net user Guest /active:no

# Disable the built-in Administrator (never the account you are logged in with)
if ($env:USERNAME -ne 'Administrator') {
    net user Administrator /active:no
} else {
    Write-Host "Logged in as Administrator - leaving it enabled." -ForegroundColor DarkYellow
}

# Show every enabled account and ask before changing any passwords
$accounts = Get-LocalUser | Where-Object { $_.Enabled }
Write-Host "Enabled local accounts:"
$accounts | ForEach-Object { Write-Host "  - $($_.Name)" }
$confirm = Read-Host "Set the SAME new password on all of these accounts? Type YES to continue (check the README first)"
if ($confirm -eq 'YES') {
    $password = Read-Host "Enter secure password for all users" -AsSecureString
    foreach ($account in $accounts) {
        try {
            Set-LocalUser -Name $account.Name -Password $password -ErrorAction Stop
        } catch {
            Write-Host "Could not change $($account.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Skipped password changes." -ForegroundColor DarkYellow
}

# Remove unauthorized users (check README first!)
# net user [UnauthorizedUser] /delete

Write-Host "User management completed" -ForegroundColor Green

# 2. PASSWORD POLICIES - Critical Points
Write-Host "`n[2/10] Setting Password Policies..." -ForegroundColor Yellow

# 'net accounts' sets history, aging, length and lockout correctly
net accounts /uniquepw:5 /maxpwage:90 /minpwage:10 /minpwlen:8 /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30

# Complexity is only available through the security policy. secedit needs the file
# saved as Unicode, otherwise /configure can fail to read it.
$cfg = Join-Path $LogDir 'secpol.cfg'
$cfgNew = Join-Path $LogDir 'secpol_new.cfg'
secedit /export /cfg "$cfg" | Out-Null
(Get-Content $cfg) -replace 'PasswordComplexity\s*=\s*\d', 'PasswordComplexity = 1' | Set-Content -Path $cfgNew -Encoding Unicode
secedit /configure /db "$env:windir\security\local.sdb" /cfg "$cfgNew" /areas SECURITYPOLICY | Out-Null
Remove-Item $cfg, $cfgNew -Force -ErrorAction SilentlyContinue

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
try { Start-Service -Name wuauserv -ErrorAction Stop } catch { Write-Host "wuauserv: $($_.Exception.Message)" }

# The policy key often does not exist yet, so create it first
$au = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
New-Item -Path $au -Force | Out-Null
Set-ItemProperty -Path $au -Name 'NoAutoUpdate' -Value 0 -Type DWord -Force
Set-ItemProperty -Path $au -Name 'AUOptions' -Value 4 -Type DWord -Force

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
    Get-Package -Name $software -ErrorAction SilentlyContinue | Uninstall-Package -Force -ErrorAction SilentlyContinue
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

# 8. DISABLE REMOTE DESKTOP (skip this step if the README says RDP is required)
Write-Host "`n[8/10] Configuring Remote Desktop..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1

Write-Host "Remote Desktop disabled" -ForegroundColor Green

# 9. USER ACCOUNT CONTROL (UAC)
Write-Host "`n[9/10] Enabling User Account Control..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2

Write-Host "UAC enabled and configured" -ForegroundColor Green

# 10. WINDOWS DEFENDER
Write-Host "`n[10/10] Configuring Windows Defender..." -ForegroundColor Yellow

Set-MpPreference -DisableRealtimeMonitoring $false
try { Update-MpSignature -ErrorAction Stop } catch { Write-Host "Signature update skipped (offline?)" -ForegroundColor DarkYellow }
# Run the scan as a background job so the script does not wait for it
Start-MpScan -ScanType QuickScan -AsJob | Out-Null

Write-Host "Windows Defender configured, quick scan started in the background" -ForegroundColor Green

Write-Host "`n=== Quick Wins Script Completed ===" -ForegroundColor Cyan
Write-Host "Check the scoring report for points!" -ForegroundColor Green
Write-Host "Log saved to: $LogDir" -ForegroundColor Cyan

Stop-Transcript
"""

# ---------------------------------------------------------------------------
# Windows Server 2019 (PowerShell)
# ---------------------------------------------------------------------------
windows_server_script = r"""#Requires -RunAsAdministrator
# CyberPatriot Quick Wins - Windows Server 2019
#
# Usage (elevated PowerShell):
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\server-wins.ps1
#
# Educational use on authorized CyberPatriot practice images only.
# Read the competition README FIRST: its authorized users and required services
# always override what this script does.

Write-Host "=== CyberPatriot - Windows Server Quick Wins ===" -ForegroundColor Cyan

$LogDir = Join-Path $env:USERPROFILE 'Desktop\CP18_Server_Logs'
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path (Join-Path $LogDir ("WindowsServer_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss')))

# 1. USER MANAGEMENT
Write-Host "`n[1/12] Managing Users..." -ForegroundColor Yellow

net user Guest /active:no
if ($env:USERNAME -ne 'Administrator') {
    net user Administrator /active:no
} else {
    Write-Host "Logged in as Administrator - leaving it enabled." -ForegroundColor DarkYellow
}

# Get-LocalUser does not exist on a domain controller, so guard it
if (Get-Command Get-LocalUser -ErrorAction SilentlyContinue) {
    try {
        $accounts = Get-LocalUser -ErrorAction Stop | Where-Object { $_.Enabled }
        Write-Host "Enabled local accounts:"
        $accounts | ForEach-Object { Write-Host "  - $($_.Name)" }
        $confirm = Read-Host "Set the SAME new password on all of these accounts? Type YES to continue (check the README first)"
        if ($confirm -eq 'YES') {
            $password = Read-Host "Enter secure password" -AsSecureString
            foreach ($account in $accounts) {
                try {
                    Set-LocalUser -Name $account.Name -Password $password -ErrorAction Stop
                } catch {
                    Write-Host "Could not change $($account.Name): $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "Skipped password changes." -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "Local user cmdlets unavailable (domain controller?). Change passwords in AD Users and Computers." -ForegroundColor DarkYellow
    }
}

Write-Host "Users configured" -ForegroundColor Green

# 2. PASSWORD POLICIES
Write-Host "`n[2/12] Setting Password Policies..." -ForegroundColor Yellow

# 'net accounts' sets history, aging, length and lockout correctly
net accounts /uniquepw:24 /maxpwage:60 /minpwage:1 /minpwlen:14 /lockoutthreshold:3 /lockoutduration:30 /lockoutwindow:30

# Complexity needs the security policy; secedit requires the file saved as Unicode
$cfg = Join-Path $LogDir 'secpol.cfg'
$cfgNew = Join-Path $LogDir 'secpol_new.cfg'
secedit /export /cfg "$cfg" | Out-Null
(Get-Content $cfg) -replace 'PasswordComplexity\s*=\s*\d', 'PasswordComplexity = 1' | Set-Content -Path $cfgNew -Encoding Unicode
secedit /configure /db "$env:windir\security\local.sdb" /cfg "$cfgNew" /areas SECURITYPOLICY | Out-Null
Remove-Item $cfg, $cfgNew -Force -ErrorAction SilentlyContinue

Write-Host "Password policies set" -ForegroundColor Green

# 3. FIREWALL
Write-Host "`n[3/12] Enabling Firewall..." -ForegroundColor Yellow

Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

Write-Host "Firewall enabled" -ForegroundColor Green

# 4. DISABLE FTP SERVICE (skip if the README says FTP is required)
Write-Host "`n[4/12] Disabling FTP Service..." -ForegroundColor Yellow

if (Get-Service -Name ftpsvc -ErrorAction SilentlyContinue) {
    Stop-Service -Name ftpsvc -Force -ErrorAction SilentlyContinue
    Set-Service -Name ftpsvc -StartupType Disabled
}

Write-Host "FTP service disabled" -ForegroundColor Green

# 5. DISABLE TELNET
Write-Host "`n[5/12] Disabling Telnet..." -ForegroundColor Yellow

# Server uses Windows Features; client editions use optional features
if (Get-Command Uninstall-WindowsFeature -ErrorAction SilentlyContinue) {
    Uninstall-WindowsFeature -Name Telnet-Client -ErrorAction SilentlyContinue | Out-Null
} else {
    Disable-WindowsOptionalFeature -Online -FeatureName TelnetClient -NoRestart -ErrorAction SilentlyContinue | Out-Null
}
foreach ($svc in 'TlntSvr', 'Telnet') {
    if (Get-Service -Name $svc -ErrorAction SilentlyContinue) {
        Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
        Set-Service -Name $svc -StartupType Disabled
    }
}

Write-Host "Telnet disabled" -ForegroundColor Green

# 6. WINDOWS UPDATES
Write-Host "`n[6/12] Enabling Windows Updates..." -ForegroundColor Yellow

Set-Service -Name wuauserv -StartupType Automatic
try { Start-Service -Name wuauserv -ErrorAction Stop } catch { Write-Host "wuauserv: $($_.Exception.Message)" }

# The policy key often does not exist yet, so create it first
$au = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
New-Item -Path $au -Force | Out-Null
Set-ItemProperty -Path $au -Name 'NoAutoUpdate' -Value 0 -Type DWord -Force
Set-ItemProperty -Path $au -Name 'AUOptions' -Value 4 -Type DWord -Force

Write-Host "Windows Updates enabled" -ForegroundColor Green

# 7. REVIEW SHARES (listed for review, never deleted automatically)
Write-Host "`n[7/12] Checking for Unauthorized Shares..." -ForegroundColor Yellow

Get-SmbShare | Where-Object { $_.Name -notlike '*$' } | ForEach-Object {
    Write-Host "Found share: $($_.Name) - Review and remove if unauthorized"
}

Write-Host "Share audit completed" -ForegroundColor Green

# 8. AUDIT POLICIES
Write-Host "`n[8/12] Enabling Audit Policies..." -ForegroundColor Yellow

auditpol /set /category:* /success:enable /failure:enable

Write-Host "Audit policies enabled" -ForegroundColor Green

# 9. DISABLE REMOTE DESKTOP (skip this step if the README says RDP is required)
Write-Host "`n[9/12] Configuring Remote Desktop..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1

Write-Host "Remote Desktop configured" -ForegroundColor Green

# 10. UAC
Write-Host "`n[10/12] Enabling UAC..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1

Write-Host "UAC enabled" -ForegroundColor Green

# 11. DISABLE UNNECESSARY FEATURES
Write-Host "`n[11/12] Disabling Unnecessary Features..." -ForegroundColor Yellow

try { Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force -ErrorAction Stop } catch { Write-Host "SMB1: $($_.Exception.Message)" }

$FeaturesToDisable = @(
    "SMB1Protocol",
    "TelnetClient",
    "TFTP"
)

foreach ($feature in $FeaturesToDisable) {
    Disable-WindowsOptionalFeature -Online -FeatureName $feature -NoRestart -ErrorAction SilentlyContinue | Out-Null
}

Write-Host "Unnecessary features disabled" -ForegroundColor Green

# 12. WINDOWS DEFENDER
Write-Host "`n[12/12] Configuring Windows Defender..." -ForegroundColor Yellow

Set-MpPreference -DisableRealtimeMonitoring $false
try { Update-MpSignature -ErrorAction Stop } catch { Write-Host "Signature update skipped (offline?)" -ForegroundColor DarkYellow }

Write-Host "Windows Defender configured" -ForegroundColor Green

Write-Host "`n=== Server Quick Wins Completed ===" -ForegroundColor Cyan
Write-Host "Log saved to: $LogDir" -ForegroundColor Cyan

Stop-Transcript
"""

# ---------------------------------------------------------------------------
# Linux Mint 21.3 (Bash)
# ---------------------------------------------------------------------------
linux_mint_script = r"""#!/bin/bash
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
"""

# ---------------------------------------------------------------------------
# Save scripts to files
# ---------------------------------------------------------------------------
scripts = {
    "windows11-wins.ps1": windows11_script,
    "server-wins.ps1": windows_server_script,
    "linux-mint-wins.sh": linux_mint_script,
}


def main():
    OUT_DIR.mkdir(exist_ok=True)
    print("CyberPatriot Quick Wins scripts\n" + "=" * 60)
    for filename, content in scripts.items():
        path = OUT_DIR / filename
        # newline="\n" keeps Unix line endings, which bash requires
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        if filename.endswith(".sh"):
            path.chmod(0o755)
        print(f"\n{filename}")
        print(f"  Lines: {len(content.splitlines())}")
        print(f"  Size:  {len(content.encode('utf-8'))} bytes")
        print(f"  Saved: {path.resolve()}")
    print("\n" + "=" * 60)
    print("Done. Read the competition README BEFORE running any script.")


if __name__ == "__main__":
    main()
