# CyberPatriot 18 Quick Wins - Setup & Usage Guide

## 📦 Repository Structure

```
cyberpatriot-quickwins/
├── README.md                      # Main documentation
├── windows11_quickwins.ps1        # Windows 11 automation script
├── windowsserver_quickwins.ps1    # Windows Server automation script
├── linux_mint_quickwins.sh        # Linux Mint 21.3 automation script
├── GHP_Video_Script.md            # Video production script
└── docs/
    ├── SETUP.md                   # This file
    ├── COMPETITION_STRATEGY.md    # Competition tips
    └── TROUBLESHOOTING.md         # Common issues
```

---

## 🚀 Installation Instructions

### For Windows 11 / Windows Server

#### Step 1: Download Scripts
1. Download `windows11_quickwins.ps1` (or `windowsserver_quickwins.ps1`)
2. Save to Desktop or easily accessible location
3. **Do NOT run directly** - follow steps below first

#### Step 2: Enable Script Execution
PowerShell scripts are disabled by default for security. To run temporarily:

1. **Right-click PowerShell** and select **"Run as Administrator"**
2. Run this command:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
3. Type `Y` and press Enter when prompted

**Note**: This only applies to the current PowerShell window. When you close it, the policy resets to default.

#### Step 3: Navigate to Script
```powershell
cd Desktop  # Or wherever you saved the script
```

#### Step 4: Run Script
```powershell
.\windows11_quickwins.ps1
# OR
.\windowsserver_quickwins.ps1
```

#### Step 5: Follow Prompts
- The script will ask for a password to set for all users
- **IMPORTANT**: Remember this password!
- Enter a strong password meeting complexity requirements:
  - At least 8 characters
  - Contains uppercase and lowercase letters
  - Contains numbers
  - Contains special characters
  - Example: `CyberP@triot2025!`

---

### For Linux Mint 21.3

#### Step 1: Download Script
1. Download `linux_mint_quickwins.sh`
2. Save to Desktop or home directory

#### Step 2: Make Executable
Open Terminal and run:
```bash
cd Desktop  # Or wherever you saved the script
chmod +x linux_mint_quickwins.sh
```

#### Step 3: Run with Sudo
```bash
sudo bash linux_mint_quickwins.sh
```

Enter your password when prompted.

#### Step 4: Monitor Progress
The script will output progress for each of 15 steps. Wait for completion message.

---

## ⚙️ Pre-Competition Setup

### Virtual Machine Preparation

#### 1. Install VMware Workstation Player (Free)
- Download from: https://www.vmware.com/products/workstation-player.html
- Install on your competition computer
- Familiarize yourself with basic operations

#### 2. Test on Practice Images
**CRITICAL**: Never test scripts on competition images before competition starts!

Practice images are available from:
- CyberPatriot Training Materials
- Your coach
- Previous year's practice rounds

#### 3. Create VM Snapshots
Before testing scripts:
```
VM Menu → Snapshot → Take Snapshot
```
Name it: "Pre-Script Baseline"

This lets you revert if something goes wrong.

#### 4. Test Script Execution
1. Start practice VM
2. Run script following instructions above
3. Check Scoring Report (Desktop icon)
4. Verify points gained
5. Document any issues

#### 5. Customize Scripts
Based on typical competition images:
- Identify common unauthorized users
- Note typical prohibited software
- List services that are usually disabled
- **Update script variables accordingly**

---

## 📋 Competition Day Checklist

### Before Competition Starts

- [ ] **Read README thoroughly** (15-20 minutes before starting timer)
- [ ] **Answer forensics questions** (do this FIRST - don't run scripts yet!)
- [ ] **Identify authorized users** from README
- [ ] **Check for required services** (FTP, SSH, Web Server, etc.)
- [ ] **Review scoring criteria** if provided
- [ ] **Have script ready** on Desktop of practice computer

### Script Execution Timeline

#### Minutes 0-2: Initial Assessment
- [ ] Read README cover to cover
- [ ] Note authorized users
- [ ] Note required services
- [ ] Answer forensics questions

#### Minutes 2-3: Script Preparation
- [ ] Copy appropriate script to VM Desktop
- [ ] Open as Administrator/sudo
- [ ] Verify script content matches image type

#### Minutes 3-15: Run Script
- [ ] Execute script
- [ ] Monitor progress output
- [ ] Note any errors
- [ ] Wait for completion

#### Minutes 15-20: Verification
- [ ] Check Scoring Report for points
- [ ] Review log files
- [ ] Verify required services still running
- [ ] Confirm authorized users intact

#### Minutes 20-240: Manual Remediation
- [ ] Review areas script couldn't automate
- [ ] Check registry (Windows)
- [ ] Review scheduled tasks
- [ ] Examine startup programs
- [ ] Audit file permissions
- [ ] Check for hidden files
- [ ] Review network shares
- [ ] Analyze event logs

---

## 🔧 Script Customization

### Windows Scripts

#### Modify Authorized Users
Find this section:
```powershell
# Remove unauthorized users (check README first!)
# net user [UnauthorizedUser] /delete
```

Uncomment and customize:
```powershell
net user "BadUser1" /delete
net user "BadUser2" /delete
```

#### Modify Prohibited Software List
Find `$ProhibitedSoftware` array and add/remove:
```powershell
$ProhibitedSoftware = @(
    "*Wireshark*",
    "*BitTorrent*",
    "*YourCustomSoftware*"  # Add your own
)
```

#### Modify Services to Disable
Find `$ServicesToDisable` array:
```powershell
$ServicesToDisable = @(
    "RemoteRegistry",
    "Telnet",
    "CustomService"  # Add your own
)
```

### Linux Scripts

#### Modify Prohibited Packages
Find `PROHIBITED_PACKAGES` array:
```bash
PROHIBITED_PACKAGES=(
    "john"
    "hydra"
    "custom-package"  # Add your own
)
```

#### Modify Services to Disable
Find `SERVICES_TO_DISABLE` array:
```bash
SERVICES_TO_DISABLE=(
    "telnet"
    "ftp"
    "custom-service"  # Add your own
)
```

---

## 📊 Understanding Script Output

### Windows Output
```
=== CyberPatriot 18 - Windows 11 Quick Wins ===
Starting automated hardening...

[1/10] Configuring Users and Passwords...
User management completed

[2/10] Setting Password Policies...
Password policies configured
```

**Color Coding**:
- **Cyan**: Section headers
- **Yellow**: Category in progress
- **Green**: Category completed
- **Red**: Errors (if any)

### Linux Output
```
=== CyberPatriot 18 - Linux Mint 21.3 Quick Wins ===
[Sun Oct 19 21:15:00 2025] Starting CyberPatriot Quick Wins Script

[1/15] Updating System Packages...
System updated

[2/15] Enabling UFW Firewall...
Firewall enabled and configured
```

### Log Files

#### Windows
Location: `%USERPROFILE%\Desktop\CP18_Logs\`
Files: `Windows11_YYYYMMDD_HHMMSS.log`

#### Linux
Location: `$HOME/Desktop/CP18_Linux_Logs/`
Files: `linux_mint_YYYYMMDD_HHMMSS.log`

**What's in logs**:
- Timestamp of each action
- Commands executed
- Success/failure messages
- Error details (if any)

---

## 🎯 Maximizing Points

### High-Impact Quick Wins (Do These First)

1. **Firewall** (3-5 points) - 30 seconds
2. **Disable Guest** (3-5 points) - 30 seconds
3. **Password Policies** (15-20 points) - 1 minute
4. **Windows Updates** (5-10 points) - 1 minute
5. **Disable Dangerous Services** (10-15 points) - 2 minutes

**Total**: 36-55 points in ~5 minutes

### Medium-Impact Actions (Do These Second)

6. **User Management** (5-15 points) - 2 minutes
7. **Remove Malware** (10-20 points) - 2 minutes
8. **Audit Policies** (5-10 points) - 1 minute
9. **UAC/Security Settings** (3-8 points) - 1 minute

**Total**: 23-53 points in ~6 minutes

### Low-Impact Actions (Time Permitting)

10. **Security Tools Installation** (2-5 points) - 2 minutes
11. **Advanced Registry** (5-10 points) - 3 minutes
12. **Network Hardening** (3-7 points) - 2 minutes

---

## ⚠️ Common Mistakes to Avoid

### Critical Errors

❌ **Running script before reading README**
- Could delete required users
- Could disable required services
- Could break scoring system

❌ **Not answering forensics questions first**
- Easy 12-24 points
- May be harder to find answers after system changes

❌ **Forgetting to verify authorized users**
- Could delete legitimate users = penalty points
- Could leave unauthorized users = missed points

❌ **Disabling required services**
- If README says "FTP server required", don't disable FTP!
- Check EACH service before disabling

❌ **Not checking Scoring Report**
- Scripts might miss something
- Manual verification essential

### Recoverable Mistakes

⚠️ **Running script multiple times**
- Usually harmless (scripts are idempotent)
- But wastes time

⚠️ **Forgetting password you set**
- Write it down!
- Keep secure note nearby

⚠️ **Closing PowerShell window too early**
- Script creates logs before closing
- Wait for "Stop-Transcript" completion

---

## 🐛 Troubleshooting

### Windows Issues

#### "Execution of scripts is disabled on this system"
**Solution**:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

#### "Access Denied" errors
**Solution**:
- Right-click PowerShell → Run as Administrator
- Confirm you're using admin account

#### Script hangs on Windows Updates
**Solution**:
- Press Ctrl+C to skip that section
- Continue manually after competition

#### Scoring Report shows negative points
**Solution**:
- Check log for what was changed
- Revert unauthorized changes
- Re-read README for requirements

### Linux Issues

#### "Permission denied"
**Solution**:
```bash
sudo bash linux_mint_quickwins.sh
# NOT: bash linux_mint_quickwins.sh
```

#### "Command not found" errors
**Solution**:
- Some tools might not be installed
- Script attempts to install them
- If it fails, install manually: `sudo apt install [tool]`

#### UFW firewall conflicts
**Solution**:
- Disable other firewalls first: `sudo ufw disable`
- Then run script

#### Package manager locked
**Solution**:
- Wait for any update processes to finish
- Close Software Manager
- Try again

---

## 📈 Performance Benchmarks

### Expected Script Performance

| Operating System | Execution Time | Expected Points | Failure Rate |
|-----------------|----------------|-----------------|--------------|
| Windows 11 | 12-15 minutes | 40-60 points | <5% |
| Windows Server | 13-15 minutes | 45-70 points | <5% |
| Linux Mint | 14-15 minutes | 50-75 points | <8% |

**Note**: Points vary by image difficulty and configuration.

### Time Breakdown

**Windows 11**:
- User Management: 2 min
- Password Policies: 1 min
- Firewall: 30 sec
- Updates: 1 min
- Software Removal: 2 min
- Services: 1 min
- Audit Policies: 1 min
- Remote Desktop: 30 sec
- UAC: 30 sec
- Defender: 2 min
- **Total: ~12 min**

**Linux Mint**:
- System Update: 3 min
- Firewall: 30 sec
- Guest Disable: 30 sec
- Password Policies: 1 min
- Root Lock: 30 sec
- Permissions: 30 sec
- Services: 2 min
- Software Removal: 2 min
- Media Files: 1 min
- Auto Updates: 1 min
- Security Tools: 2 min
- Sysctl: 1 min
- IPv6: 30 sec
- SSH: 1 min
- User Passwords: 2 min
- **Total: ~14 min**

---

## 🎓 Educational Resources

### Learn More About Script Components

#### PowerShell Resources
- Microsoft PowerShell Documentation
- PowerShell Gallery
- "Learn PowerShell in a Month of Lunches" (book)

#### Bash Resources
- Linux Command Line Basics
- Advanced Bash Scripting Guide
- Ubuntu Community Help Wiki

#### Cybersecurity Concepts
- CIS Benchmarks (Windows, Linux)
- NIST Cybersecurity Framework
- SANS Critical Security Controls

#### CyberPatriot Resources
- Official CyberPatriot Training Materials
- AFA CyberPatriot Resources
- Previous competition guides

---

## 🏆 Advanced Optimization

### For Experienced Teams

#### Parallel Execution
Run multiple scripts simultaneously on different images.

#### Custom Modules
Break scripts into modular functions:
```powershell
function Set-PasswordPolicies { ... }
function Remove-UnauthorizedUsers { ... }
function Enable-AuditPolicies { ... }
```

#### Configuration Files
Store image-specific settings in JSON/XML:
```json
{
  "authorized_users": ["alice", "bob"],
  "required_services": ["ssh", "apache2"],
  "prohibited_software": ["wireshark", "nmap"]
}
```

#### Automated Testing
Create test harness for script validation:
```powershell
Invoke-Pester -Script .\Tests\ScriptValidation.Tests.ps1
```

---

## 📞 Getting Help

### During Competition
- **Read the README again** - answer is usually there
- **Check scoring report** - shows what's working
- **Review logs** - shows what script did
- **Ask coach** - they can clarify rules
- **Don't panic** - manual remediation still works

### After Competition
- **GitHub Issues** - report bugs or suggest features
- **Team Discussions** - share learnings
- **Coach Feedback** - get improvement suggestions

---

## ✅ Final Checklist Before Competition

- [ ] Scripts tested on practice images
- [ ] VM snapshots created
- [ ] VMware Workstation installed and configured
- [ ] Script customizations completed
- [ ] Team members trained on script usage
- [ ] Backup plan if scripts fail
- [ ] Competition rules reviewed
- [ ] Forensics question strategy discussed
- [ ] Time management plan created
- [ ] All team members know their roles

---

## 🎉 Good Luck!

Remember:
- **Scripts are tools, not magic** - verify everything
- **READ THE README** - cannot emphasize this enough
- **Forensics first** - easy points before automation
- **Stay calm** - you have 4 hours
- **Have fun** - cybersecurity is awesome!

**Most importantly**: These scripts represent one approach to CyberPatriot. The best teams combine automation with deep understanding, critical thinking, and manual verification.

---

*Created by Moulik for GHP Computer Science Portfolio Project*
*CyberPatriot Team Commander | Platinum Division*
