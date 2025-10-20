# CyberPatriot 18 - Windows 11 Quick Wins Script
# Run as Administrator
# Created for GHP Computer Science Portfolio

Write-Host "=== CyberPatriot 18 - Windows 11 Quick Wins ===" -ForegroundColor Cyan
Write-Host "Starting automated hardening..." -ForegroundColor Green

# Create log directory
$LogDir = "$env:USERPROFILE\Desktop\CP18_Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path "$LogDir\Windows11_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

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

secedit /export /cfg $LogDir\secpol.cfg | Out-Null
(Get-Content $LogDir\secpol.cfg) -replace 'PasswordHistorySize = \d+', 'PasswordHistorySize = 5' `
    -replace 'MaximumPasswordAge = \d+', 'MaximumPasswordAge = 90' `
    -replace 'MinimumPasswordAge = \d+', 'MinimumPasswordAge = 10' `
    -replace 'MinimumPasswordLength = \d+', 'MinimumPasswordLength = 8' `
    -replace 'PasswordComplexity = \d', 'PasswordComplexity = 1' `
    -replace 'LockoutBadCount = \d+', 'LockoutBadCount = 5' | Set-Content $LogDir\secpol_new.cfg
secedit /configure /db c:\windows\security\local.sdb /cfg $LogDir\secpol_new.cfg /areas SECURITYPOLICY | Out-Null
Remove-Item $LogDir\secpol.cfg, $LogDir\secpol_new.cfg -Force

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
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "NoAutoUpdate" -Value 0 -Force
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Name "AUOptions" -Value 4 -Force

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
Update-MpSignature
Start-MpScan -ScanType QuickScan

Write-Host "Windows Defender configured and scanning" -ForegroundColor Green

Write-Host "`n=== Quick Wins Script Completed ===" -ForegroundColor Cyan
Write-Host "Check the scoring report for points!" -ForegroundColor Green
Write-Host "Log saved to: $LogDir" -ForegroundColor Cyan

Stop-Transcript
