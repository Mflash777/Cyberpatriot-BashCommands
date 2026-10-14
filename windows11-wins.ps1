#Requires -RunAsAdministrator
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
