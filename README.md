# CyberPatriot 18 Quick Wins Automation Scripts

**Created by Moulik for GHP Computer Science Portfolio**

## 📋 Overview

This repository contains automated  hardening scripts for CyberPatriot 18 competition, designed to maximize points in the first 15 minutes of competition. The scripts are optimized for:

- **Windows 11** (Desktop)
- **Windows Server 2019** (Server Environment)
- **Linux Mint 21.3** (Linux Desktop)

## 🎯 Purpose

These scripts demonstrate practical cybersecurity automation by implementing industry-standard security hardening techniques. They showcase:

- **System Administration**: Automated user management, password policies, and service configuration
- **Cybersecurity**: Implementing defense-in-depth strategies through multiple security layers
- **Scripting**: PowerShell and Bash automation for rapid deployment
- **Competition Strategy**: Maximizing efficiency through prioritized vulnerability remediation

## 🚀 Quick Start

### Windows 11 & Windows Server

1. **Right-click PowerShell** and select "Run as Administrator"
2. Enable script execution:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
3. Run the appropriate script:
   ```powershell
   .\windows11_quickwins.ps1
   # OR
   .\windowsserver_quickwins.ps1
   ```

### Linux Mint 21.3

1. **Make script executable**:
   ```bash
   chmod +x linux_mint_quickwins.sh
   ```
2. **Run with sudo**:
   ```bash
   sudo bash linux_mint_quickwins.sh
   ```

## 📊 Features & Points Breakdown

### Windows 11 Script (10 Categories)

| Category | Points Impact | Time |
|----------|---------------|------|
| User Management | High | ~2 min |
| Password Policies | Critical | ~1 min |
| Windows Firewall | High | ~30 sec |
| Windows Updates | High | ~1 min |
| Remove Malware | Variable | ~2 min |
| Disable Services | Medium | ~1 min |
| Audit Policies | Medium | ~1 min |
| Remote Desktop | Low | ~30 sec |
| UAC Configuration | Medium | ~30 sec |
| Windows Defender | High | ~2 min |

**Estimated Total Time**: 12-15 minutes  
**Expected Points**: 40-60 points (varies by image)

### Windows Server Script (12 Categories)

| Category | Points Impact | Time |
|----------|---------------|------|
| User Management | High | ~2 min |
| Password Policies | Critical | ~1 min |
| Firewall | High | ~30 sec |
| Disable FTP | High | ~30 sec |
| Disable Telnet | High | ~30 sec |
| Windows Updates | High | ~1 min |
| Remove Shares | Variable | ~2 min |
| Audit Policies | Medium | ~1 min |
| Remote Desktop | Low | ~30 sec |
| UAC | Medium | ~30 sec |
| Disable Features | Medium | ~1 min |
| Windows Defender | High | ~2 min |

**Estimated Total Time**: 13-15 minutes  
**Expected Points**: 45-70 points (varies by image)

### Linux Mint Script (15 Categories)

| Category | Points Impact | Time |
|----------|---------------|------|
| System Updates | Critical | ~3 min |
| UFW Firewall | High | ~30 sec |
| Disable Guest | High | ~30 sec |
| Password Policies | Critical | ~1 min |
| Lock Root | High | ~30 sec |
| File Permissions | Medium | ~30 sec |
| Disable Services | High | ~2 min |
| Remove Malware | Variable | ~2 min |
| Find Media Files | Variable | ~1 min |
| Auto Updates | High | ~1 min |
| Security Tools | Medium | ~2 min |
| Sysctl Config | Medium | ~1 min |
| Disable IPv6 | Low | ~30 sec |
| Secure SSH | Medium | ~1 min |
| User Passwords | High | ~2 min |

**Estimated Total Time**: 14-15 minutes  
**Expected Points**: 50-75 points (varies by image)

## ⚠️ Important Notes

### Before Running Scripts

1. **READ THE README**: Always read the competition README first
2. **Answer Forensics Questions**: Do this BEFORE running scripts (12-24 points each)
3. **Check Authorized Users**: Verify which users should exist
4. **Required Services**: Check if specific services (FTP, SSH, etc.) are required
5. **Backup**: Scripts create logs but don't backup system state

### Critical Competition Rules

- **NO INTERNET TOOLS**: These scripts don't download external tools
- **MANUAL VERIFICATION**: Always verify script results
- **README COMPLIANCE**: Scripts are templates - customize based on README
- **AUTHORIZED USE**: Only use on practice images or with permission

### After Running Scripts

1. Check the **Scoring Report** (Desktop icon)
2. Review the **log files** created on Desktop
3. Answer any **remaining forensics questions**
4. **Manually verify**:
   - Unauthorized users removed
   - Required services still running
   - Prohibited software deleted
   - Media files removed
5. Continue with **deep analysis**:
   - Registry checks
   - Scheduled tasks
   - Startup programs
   - Network shares
   - File permissions

## 🔍 Script Architecture

### Design Philosophy

These scripts follow a **prioritized remediation strategy**:

1. **Quick Wins First** (1-5 minutes):
   - Enable firewall
   - Disable dangerous services
   - Set password policies

2. **High-Impact Security** (5-10 minutes):
   - User management
   - Remove malware
   - Enable updates

3. **Comprehensive Hardening** (10-15 minutes):
   - Audit policies
   - System configuration
   - Security tools

### Logging & Transparency

All scripts create detailed logs:
- **Windows**: `%USERPROFILE%\Desktop\CP18_Logs\`
- **Linux**: `$HOME/Desktop/CP18_Linux_Logs/`

Logs include:
- Timestamp of each action
- Commands executed
- Success/failure status
- Files modified

## 🛠️ Technologies Used

- **PowerShell 5.1+**: Windows automation
- **Bash 4.0+**: Linux automation
- **Windows Security APIs**: Local security policy, user management
- **Linux PAM**: Password authentication modules
- **Systemd/Service Management**: Service control
- **UFW**: Uncomplicated Firewall (Linux)
- **Windows Defender**: Antimalware scanning

## 📚 Educational Value

This project demonstrates:

### Computer Science Concepts
- **Automation**: Reducing manual tasks through scripting
- **Error Handling**: Graceful failures and logging
- **Systems Programming**: Interacting with OS APIs
- **Security Engineering**: Defense-in-depth implementation

### Cybersecurity Principles
- **Least Privilege**: Disabling unnecessary access
- **Defense in Depth**: Multiple security layers
- **Hardening**: Reducing attack surface
- **Audit & Compliance**: Logging and monitoring

### Real-World Applications
- **Enterprise Security**: Scripts similar to production hardening
- **Incident Response**: Rapid remediation techniques
- **Compliance**: Meeting security baselines (CIS, NIST)
- **DevSecOps**: Infrastructure as Code for security


## 🔐 Security Considerations

### What These Scripts DO

✅ Implement CIS-aligned security hardening  
✅ Follow Microsoft and Linux security best practices  
✅ Create audit trails through logging  
✅ Enable protective security features  
✅ Remove common attack vectors  

### What These Scripts DON'T Do

❌ Guarantee 100% security  
❌ Replace manual security analysis  
❌ Work on every possible image configuration  
❌ Bypass competition detection mechanisms  
❌ Download or install external tools during competition  

## 🏆 Competition Strategy

### First 15 Minutes Plan

1. **[0-2 min]** Read README, answer forensics questions
2. **[2-3 min]** Run appropriate quick wins script
3. **[3-5 min]** Monitor script execution, check logs
4. **[5-7 min]** Verify scoring report for points
5. **[7-10 min]** Manual user/software verification
6. **[10-15 min]** Address script-missed items

### After Quick Wins (Remaining Time)

- Deep dive into services
- Registry analysis (Windows)
- Cron jobs and scheduled tasks
- File permission audits
- Network configuration review
- Application-specific hardening

## 📜 License & Ethics

**Educational Use Only**: These scripts are for learning and authorized CyberPatriot practice images only.

**Competition Ethics**: 
- Scripts must be written by team members
- Use only on practice images during learning
- Follow all CyberPatriot rules during competition
- Don't share scripts with other teams

## 👨‍💻 Author

**Moulik**  
High School Student | Georgia  
CyberPatriot Team Commander | FRC Robotics Programmer  

**Background**:
- Founded school CyberPatriot club, reached Platinum Division
- FRC Robotics Team programmer (Java)
- Cyber camp graduate (Windows, Linux, Cisco, Python drones)
- Stellar Explorers aerospace coding team

**GHP Interests**: Artificial Intelligence, Cybersecurity, Computer Systems

## 🔗 Related Projects

- CyberPatriot Training Tool Development
- Autonomous Robotics Programming (FRC, FLL)
- Python Drone Automation
- AI-Powered Applications

## 📧 Contact

For questions about this project or GHP application:
- GitHub: [See repository]
- Purpose: Educational demonstration for GHP Computer Science portfolio

---

**Note**: This project was created specifically for the Governor's Honors Program Computer Science application to demonstrate practical cybersecurity knowledge, automation skills, and real-world problem-solving in a competitive environment.
