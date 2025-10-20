# CyberPatriot 18 - Windows Server Quick Wins Script
# Run as Administrator
# Created for GHP Computer Science Portfolio

Write-Host "=== CyberPatriot 18 - Windows Server Quick Wins ===" -ForegroundColor Cyan

$LogDir = "$env:USERPROFILE\Desktop\CP18_Server_Logs"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
Start-Transcript -Path "$LogDir\WindowsServer_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

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

secedit /export /cfg $LogDir\secpol.cfg | Out-Null
(Get-Content $LogDir\secpol.cfg) -replace 'PasswordHistorySize = \d+', 'PasswordHistorySize = 24' `
    -replace 'MaximumPasswordAge = \d+', 'MaximumPasswordAge = 60' `
    -replace 'MinimumPasswordAge = \d+', 'MinimumPasswordAge = 1' `
    -replace 'MinimumPasswordLength = \d+', 'MinimumPasswordLength = 14' `
    -replace 'PasswordComplexity = \d', 'PasswordComplexity = 1' `
    -replace 'LockoutBadCount = \d+', 'LockoutBadCount = 3' | Set-Content $LogDir\secpol_new.cfg
secedit /configure /db c:\windows\security\local.sdb /cfg $LogDir\secpol_new.cfg /areas SECURITYPOLICY | Out-Null

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

Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1

Write-Host "Remote Desktop configured" -ForegroundColor Green

# 10. UAC
Write-Host "`n[10/12] Enabling UAC..." -ForegroundColor Yellow

Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1

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
