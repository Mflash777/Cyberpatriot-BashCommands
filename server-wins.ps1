#Requires -RunAsAdministrator
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
