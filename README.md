# CyberPatriot Quick Wins Automation Scripts

Automated first-15-minutes hardening scripts for CyberPatriot practice images, written by Moulik Suhag.

| Script | Target image |
| --- | --- |
| `windows11-wins.ps1` | Windows 11 |
| `server-wins.ps1` | Windows Server 2019 |
| `linux-mint-wins.sh` | Linux Mint 21.3 |

> **Educational use only.** Run these on authorized CyberPatriot practice images. The competition README always overrides the scripts: authorized users and required services come first.

## Why this exists

In CyberPatriot, a team gets several vulnerable virtual machines and four hours. The first 10-15 minutes are the most valuable, and they are also where manual work causes the most mistakes: forgotten settings, inconsistent steps, and lost points. These scripts turn the repeatable baseline steps into one command so the team can spend its time on the harder, image-specific vulnerabilities.

## Quick start

### Windows 11 / Windows Server

1. Right-click PowerShell and choose **Run as Administrator**.
2. Allow scripts for this window only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. Run the script for your image:

   ```powershell
   .\windows11-wins.ps1
   # or
   .\server-wins.ps1
   ```

The script lists every enabled account and asks you to type `YES` before it changes any passwords.

### Linux Mint 21.3

```bash
sudo bash linux-mint-wins.sh
# or, to skip the two slowest steps (full upgrade, installing scanners):
sudo bash linux-mint-wins.sh --fast
```

## What each script does

### Windows 11 (10 steps)

1. Disable Guest and the built-in Administrator (never the account you are logged in as); optionally set new passwords
2. Password and lockout policy (`net accounts`) plus password complexity (`secedit`)
3. Enable Windows Defender Firewall on all profiles
4. Enable the Windows Update service and automatic update policy
5. Uninstall a list of prohibited software
6. Disable legacy services (RemoteRegistry, Telnet, FTP, SNMP)
7. Enable audit policies
8. Disable Remote Desktop
9. Enable UAC
10. Turn on Defender real-time protection, update signatures, start a background quick scan

### Windows Server (12 steps)

Same core as Windows 11, plus: stricter password policy (14 characters, 24 remembered), FTP and Telnet removal, SMB1 disabled, a share audit that lists shares for review, and a guard for domain controllers (which have no local users).

### Linux Mint (15 steps)

1. System update (skipped with `--fast`)
2. UFW firewall: default deny incoming, logging on
3. Disable the guest login (LightDM)
4. Password aging, complexity (`pam_pwquality`), history, and account lockout
5. Lock the root account
6. Correct permissions on `/etc/shadow`, `/etc/passwd`, `/etc/group`
7. Stop and disable risky services
8. Purge a list of prohibited packages
9. List media files for review (not deleted)
10. Enable automatic updates
11. Install ClamAV, rkhunter, chkrootkit (skipped with `--fast`)
12. Network hardening with `sysctl` (spoofing protection, redirects, SYN cookies)
13. Disable IPv6
14. Harden SSH (validated with `sshd -t` before restarting)
15. Remind you to set user passwords manually

## Design choices

- **Prioritized.** Quick, high-value settings first; slower or riskier ones later.
- **Human in the loop.** The scripts list users, shares, and media files for review instead of deleting them, and they ask before changing passwords. Only the README knows who is authorized.
- **Safe to re-run.** Config edits are guarded or replaced rather than stacked.
- **Fails safe.** The Linux script backs up each file it edits (`*.backup`), checks that a PAM module exists before referencing it, and validates the SSH config before restarting the service.
- **Logged.** Every run writes a timestamped log to the Desktop (`CP18_Logs`, `CP18_Server_Logs`, `CP18_Linux_Logs`).

The settings follow common hardening guidance (CIS-style baselines and NIST recommendations) but are not a full implementation of any benchmark.

## Before and after you run a script

**Before:** read the competition README, answer forensics questions, note the authorized users, and note any required services (FTP, SSH, web server, RDP). Take a VM snapshot.

**After:** check the scoring report, review the log, then continue manually with scheduled tasks, startup items, shares, registry, and file permissions. Verify that no authorized user or required service was affected.

## Known limitations

- Template values (prohibited software, services to disable) are generic. Edit the lists at the top of each section to match the README.
- Audit policy commands use English category names.
- Linux steps 1, 10, and 11 need access to the package repositories.
- Scripts do not replace manual analysis and will not catch image-specific vulnerabilities.

## Roadmap

- Network-level security checks
- Automated vulnerability scanning
- A dashboard that shows an image's security status in real time

## Ethics

Scripts must be written by team members, used on practice images only, and used in line with all CyberPatriot rules. Do not share competition-specific material with other teams.

## Technologies

PowerShell 5.1+, Bash, Windows Defender and Windows Firewall, `secedit` and `auditpol`, Linux PAM, `sysctl`, UFW, systemd.
