# CyberPatriot Quick Wins: Setup, Usage and Verification Guide

By Moulik Suhag. Educational use on authorized CyberPatriot practice images only. The competition README always overrides these scripts: authorized users and required services come first.

## Contents

1. [Repository structure](#1-repository-structure)
2. [What has been tested, and what you must test yourself](#2-testing-status)
3. [Before you run anything](#3-before-you-run-anything)
4. [Running the scripts](#4-running-the-scripts)
5. [Verify that every change worked](#5-verify-that-every-change-worked)
6. [Test log template](#6-test-log-template)
7. [Competition-day timeline](#7-competition-day-timeline)
8. [Customizing the scripts](#8-customizing-the-scripts)
9. [Understanding the output and logs](#9-understanding-the-output-and-logs)
10. [Common mistakes](#10-common-mistakes)
11. [Troubleshooting](#11-troubleshooting)
12. [Limitations](#12-limitations)

---

## 1. Repository structure

```
Cyberpatriot-BashCommands/
├── README.md              # Overview and quick start
├── SETUP-GUIDE.md         # This file
├── windows11-wins.ps1     # Windows 11 (10 steps)
├── server-wins.ps1        # Windows Server 2019 (12 steps)
└── linux-mint-wins.sh     # Linux Mint 21.3 (15 steps, optional --fast)
```

---

## 2. Testing status

Being honest about this is part of the project. Here is what each level of testing means.

| Check | Linux script | Windows scripts |
| --- | --- | --- |
| Syntax check (`bash -n`) | Passed | Not applicable |
| Editing logic tested on copies of sample config files (login.defs, PAM, sshd_config, sysctl) | Done, including running the edits twice to confirm nothing is duplicated | Not applicable |
| Reviewed line by line for known failure modes (see below) | Done | Done |
| Run end to end on a real practice VM | **You must do this** (Section 6) | **You must do this** (Section 6) |

The Windows scripts could not be executed on Windows while they were being fixed, so treat them as reviewed but unproven until you complete the test log in Section 6 on your own VMs. Nothing in this guide claims a point total, because points depend on the image.

### Problems found and fixed during review

| Script | Original problem | Fix |
| --- | --- | --- |
| Linux | Account lockout line named `pam_tally2.so` even if the module was missing, which can lock every user out | Only added if the module file exists; placed before the `pam_unix` line; lockout counter reset added to `common-account` |
| Linux | `dpkg-reconfigure unattended-upgrades` opens an interactive prompt and freezes the script | Writes `/etc/apt/apt.conf.d/20auto-upgrades` directly |
| Linux | Package check matched by prefix, so `nmap` would also match unrelated libraries | Exact match with `dpkg-query` |
| Linux | Settings appended every run, so config files grew | Blocks wrapped in `BEGIN`/`END` markers and replaced on re-run |
| Linux | SSH edits could break the server config | Old lines removed, new ones added first, `sshd -t` validates, backup restored if invalid |
| Linux | Log folder landed in `/root` under `sudo` | Uses the real user's Desktop through `SUDO_USER` |
| Linux | Backup overwritten on second run | A `.backup` is only created once, so you always keep the original |
| Windows | Password complexity file saved in the wrong encoding, so `secedit` could not read it | Saved as Unicode |
| Windows | Windows Update policy key often missing, so setting values failed | Key created first |
| Windows | Same password set on every account without checking | Lists accounts and requires typing `YES` |
| Windows | Script could disable the account you are logged in as | Skipped when logged in as `Administrator` |
| Windows | Full Defender scan blocked the script | Quick scan runs as a background job |
| Server | Crashed on domain controllers (no local users) | Guarded with a command check |

---

## 3. Before you run anything

### 3.1 Build a safe test setup

1. Install **VMware Workstation Player** (free for personal use) or VMware Workstation.
2. Get **practice images** from your coach or the official CyberPatriot training materials. Never test on a live competition image.
3. Start the VM, let it fully boot, then take a snapshot: **VM → Snapshot → Take Snapshot**, named `Pre-Script Baseline`.
4. Copy the script into the VM (drag and drop, a shared folder, or `git clone`).

### 3.2 Read the README first

Before any script runs:

- [ ] Read the competition README completely.
- [ ] Write down the **authorized users** and which are administrators.
- [ ] Write down **required services** (FTP, SSH, web server, RDP and so on). Each is a step you may need to skip or edit.
- [ ] Answer the **forensics questions first**. Scripts can change the evidence they ask about.

---

## 4. Running the scripts

### 4.1 Windows 11 and Windows Server 2019

1. Right-click PowerShell and choose **Run as Administrator**. (The scripts have `#Requires -RunAsAdministrator` and refuse to start otherwise.)
2. Allow scripts for this window only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

   This lasts only until you close the window.
3. Go to the folder with the script:

   ```powershell
   cd $env:USERPROFILE\Desktop
   ```

4. Run the one for your image:

   ```powershell
   .\windows11-wins.ps1
   # or
   .\server-wins.ps1
   ```

5. At the prompt, the script **lists every enabled account**. Compare the list with the README. Type `YES` only if you want the same new password on all of them. Anything else skips password changes.
6. If you type `YES`, choose a password that meets complexity rules (for example 14 or more characters on Server, with upper case, lower case, a number and a symbol), and write it down.
7. Wait for the final lines (`Quick Wins Completed` and `Log saved to:`). The transcript is only fully written once the script finishes.

### 4.2 Linux Mint 21.3

```bash
cd ~/Desktop
sudo bash linux-mint-wins.sh          # full run
sudo bash linux-mint-wins.sh --fast   # skips the system upgrade and scanner install
```

- Use `--fast` when you want results quickly. Steps 1 and 11 are the slow ones. You can run them later by hand.
- Run it with `sudo bash`, not plain `bash`. The script exits with a message if it is not root.
- When it finishes, **open a second terminal and run `sudo -k; sudo true`**. If sudo still works, the PAM edits did not lock you out. Do this before closing the first terminal.

### 4.3 What the scripts deliberately do *not* do

| Not automated | Why |
| --- | --- |
| Deleting users | Only the README knows who is authorized. Removing a legitimate user costs points. |
| Deleting media files and shares | Listed for review (`media_files.txt`, share audit). Files may be needed or part of a forensics question. |
| Setting Linux user passwords | Done by hand with `passwd <user>` after reading the README. |

---

## 5. Verify that every change worked

Do not trust the script's "done" messages alone. Each section below gives a command that proves a change actually took effect. Run them in the VM after the script finishes, then record the results in Section 6.

### 5.1 Linux Mint

| Step | What it does | How to verify | Expected result |
| --- | --- | --- | --- |
| 1 | Updates packages | `apt list --upgradable 2>/dev/null \| wc -l` | Close to 1 (just the header) |
| 2 | UFW firewall | `sudo ufw status verbose` | `Status: active`, `Default: deny (incoming), allow (outgoing)`, `Logging: on` |
| 3 | Disables guest login | `cat /etc/lightdm/lightdm.conf.d/50-no-guest.conf` and `grep allow-guest /etc/lightdm/lightdm.conf` | `allow-guest=false` in both (second file may not exist) |
| 4 | Password aging | `grep -E '^PASS_(MAX\|MIN\|WARN)' /etc/login.defs` | 90, 10, 7 |
| 4 | Complexity and history | `grep -E 'pwquality\|pam_unix' /etc/pam.d/common-password` | `minlen=8 ucredit=-1 ...` on the pwquality line and `remember=5` on `pam_unix` |
| 4 | Lockout | `grep tally /etc/pam.d/common-auth /etc/pam.d/common-account` | Lines present if `pam_tally2` exists, otherwise a message saying configure `pam_faillock` manually |
| 5 | Root locked | `sudo passwd -S root` | Second field is `L` |
| 6 | Permissions | `stat -c '%a %n' /etc/shadow /etc/passwd /etc/group` | `640`, `644`, `644` |
| 7 | Services off | `systemctl is-enabled apache2 vsftpd smbd 2>&1` | `disabled` or `not-found` |
| 8 | Packages removed | `dpkg -l john hydra nmap 2>&1 \| grep ^ii` | No output |
| 9 | Media list | `cat ~/Desktop/CP18_Linux_Logs/media_files.txt` | A list (can be empty) |
| 10 | Auto updates | `cat /etc/apt/apt.conf.d/20auto-upgrades` | Both lines set to `"1"` |
| 11 | Scanners | `which clamscan rkhunter chkrootkit` | Three paths (not in `--fast` mode) |
| 12 | Kernel settings | `sysctl net.ipv4.tcp_syncookies net.ipv4.conf.all.rp_filter` | Both `= 1` |
| 13 | IPv6 off | `sysctl net.ipv6.conf.all.disable_ipv6` | `= 1` |
| 14 | SSH | `sudo sshd -t && head -2 /etc/ssh/sshd_config` | No error and the first two lines say `PermitRootLogin no` and `PermitEmptyPasswords no` |
| All | Re-run safety | Run the script a second time, then `grep -c 'BEGIN CP-QUICKWINS' /etc/sysctl.conf` | `1` (not 2) |
| All | Backups exist | `ls /etc/*.backup /etc/pam.d/*.backup` | One `.backup` per edited file |

### 5.2 Windows 11

Run these in an elevated PowerShell.

| Step | What it does | How to verify | Expected result |
| --- | --- | --- | --- |
| 1 | Guest and Administrator off | `net user Guest` and `net user Administrator` | `Account active   No` (unless you were logged in as Administrator) |
| 2 | Password and lockout policy | `net accounts` | History 5, max age 90, min age 10, min length 8, lockout threshold 5, duration 30, window 30 |
| 2 | Complexity | `secedit /export /cfg $env:TEMP\c.cfg; Select-String PasswordComplexity $env:TEMP\c.cfg` | `PasswordComplexity = 1` |
| 3 | Firewall | `Get-NetFirewallProfile \| Select Name,Enabled` | `True` for Domain, Private, Public |
| 4 | Windows Update | `Get-Service wuauserv` and `Get-ItemProperty HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU` | Service startup Automatic; `NoAutoUpdate = 0`, `AUOptions = 4` |
| 5 | Software removal | `Get-Package *Wireshark*,*Nmap*` | No results |
| 6 | Services disabled | `Get-Service RemoteRegistry,SNMP,TlntSvr -ErrorAction SilentlyContinue \| Select Name,StartType` | `Disabled` |
| 7 | Audit policy | `auditpol /get /category:*` | Success and Failure for the five categories set |
| 8 | Remote Desktop | `(Get-ItemProperty 'HKLM:\System\CurrentControlSet\Control\Terminal Server').fDenyTSConnections` | `1` |
| 9 | UAC | `(Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System).EnableLUA` | `1` |
| 10 | Defender | `Get-MpComputerStatus \| Select RealTimeProtectionEnabled,AntivirusSignatureLastUpdated` | Real-time `True`; signatures recent if the VM is online |

### 5.3 Windows Server 2019

Use the Windows 11 table for password policy, firewall, updates, audit policy, Remote Desktop, UAC and Defender, with these differences:

| Step | Difference | How to verify | Expected result |
| --- | --- | --- | --- |
| 2 | Stricter policy | `net accounts` | History 24, max age 60, min age 1, min length 14, lockout threshold 3 |
| 4 | FTP service | `Get-Service ftpsvc -ErrorAction SilentlyContinue` | Missing or Disabled |
| 5 | Telnet | `Get-WindowsFeature Telnet-Client` | `Available` (not Installed) |
| 7 | Share audit | Read the console output | Lists non-admin shares for you to review |
| 8 | Audit policy | `auditpol /get /category:*` | All categories set to Success and Failure |
| 11 | SMB1 | `Get-SmbServerConfiguration \| Select EnableSMB1Protocol` | `False` |

### 5.4 Confirm with the official scoring report

The CyberPatriot scoring report on the image is the final check. After the script finishes (give it a minute to refresh), check that:

- New points appeared for the settings you expected.
- No **penalty** appeared (for example a required service stopped or an authorized user affected).
- If a step did not score, use Section 5 to confirm the setting is actually in place. If it is, the image may not check that item.

---

## 6. Test log template

Copy this table into a note and fill it in for each practice image you try. Keeping it in the repo (for example as `TEST-LOG.md`) is what lets you show, and not just claim, that the scripts work.

| Field | Entry |
| --- | --- |
| Date | |
| Script and version (commit) | |
| Image name and OS | |
| Snapshot reverted before test? | Yes / No |
| Run time (start to finish) | |
| Points before / after | |
| Steps that worked (from Section 5) | |
| Steps that failed or errored | |
| Required service or user affected? | Yes / No (details) |
| Re-run produced duplicates? | Yes / No |
| Fix made afterwards | |

Suggested minimum before you rely on a script in a competition:

- [ ] One clean run on a fresh snapshot, with Section 5 checks passed.
- [ ] A second run on the same machine (proves it is safe to repeat).
- [ ] A run on an image that **requires** a service (such as SSH or FTP) so you practice editing the script to keep it.
- [ ] A run offline, to see which steps degrade gracefully.

---

## 7. Competition-day timeline

| Time | Action |
| --- | --- |
| Before the timer | Read the README, list authorized users, list required services, note anything the script must skip |
| 0 to 15 min | Answer the forensics questions **first** |
| 15 to 20 min | Edit the script lists to match the README, take a VM snapshot, run the script |
| 20 to 30 min | Run the Section 5 checks, open the scoring report, confirm no penalties |
| 30 min to the end | Manual work: scheduled tasks, startup items, shares, file permissions, hidden or unauthorized files, event logs, user accounts and groups |

---

## 8. Customizing the scripts

### 8.1 Windows

Remove unauthorized users (only after reading the README), near the top of the user section:

```powershell
net user "BadUser1" /delete
net user "BadUser2" /delete
```

Prohibited software (`$ProhibitedSoftware` array in `windows11-wins.ps1`):

```powershell
$ProhibitedSoftware = @(
    "*Wireshark*",
    "*BitTorrent*",
    "*YourCustomSoftware*"
)
```

Services to disable (`$ServicesToDisable`). **Delete any service the README says is required.**

Skip Remote Desktop hardening if RDP is required by deleting or commenting out the `fDenyTSConnections` line.

### 8.2 Linux

Edit the arrays near the top of steps 7 and 8:

```bash
SERVICES_TO_DISABLE=( "telnet" "ftp" "vsftpd" "apache2" ... )
PROHIBITED_PACKAGES=( "john" "hydra" "nmap" ... )
```

If the README requires a service (for example `apache2` or `vsftpd`), **remove it from `SERVICES_TO_DISABLE`**.

Other lines you may need to change:

- Step 12 sets `net.ipv4.icmp_echo_ignore_all = 1`, which makes the machine ignore ping. Remove that line if a scored check or a required service depends on ping.
- Step 13 disables IPv6. Skip it if the README requires IPv6.
- Step 14 only runs if SSH is installed, and does not turn off password logins. Add your own `PasswordAuthentication` rule if the README says to.

---

## 9. Understanding the output and logs

### Console colors (Windows)

- **Cyan**: section headers
- **Yellow**: step in progress
- **Green**: step done
- **Red**: an error to read

### Logs

| OS | Location | File |
| --- | --- | --- |
| Windows 11 | `Desktop\CP18_Logs\` | `Windows11_YYYYMMDD_HHMMSS.log` |
| Windows Server | `Desktop\CP18_Server_Logs\` | `WindowsServer_YYYYMMDD_HHMMSS.log` |
| Linux | `~/Desktop/CP18_Linux_Logs/` | `linux_mint_YYYYMMDD_HHMMSS.log` and `media_files.txt` |

Logs hold every command's output and any errors, so they let you explain exactly what changed. On Linux, the original version of every edited file is kept next to it as `<name>.backup`.

---

## 10. Common mistakes

**Critical**

- Running a script before reading the README (could stop a required service or break an authorized user).
- Skipping the forensics questions (easy points that automation can erase).
- Setting one password on all accounts without checking the account list.
- Closing the Linux terminal before confirming `sudo` still works.
- Not checking the scoring report for penalties.

**Recoverable**

- Running the script twice. It is designed to be safe to repeat, but it wastes time.
- Forgetting the password you set. Write it down.
- Closing PowerShell before the script prints `Log saved to:`.

---

## 11. Troubleshooting

### Windows

| Problem | Fix |
| --- | --- |
| "Running scripts is disabled" | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the same window |
| Script says it requires administrator | Close it and reopen PowerShell with **Run as Administrator** |
| Windows Update service will not start | The script prints the error and continues. Start it manually later. |
| Defender signature update skipped | The VM is offline. This is expected. |
| `secedit` error | Re-run in an elevated window; check that the log folder is writable |
| Penalty in the scoring report | Read the log, find the matching step, revert it, and re-read the README |

### Linux

| Problem | Fix |
| --- | --- |
| "Please run as root" | Use `sudo bash linux-mint-wins.sh` |
| `apt` is locked | Wait for other update processes, close Software Manager, try again |
| Steps 1, 10 or 11 fail | The image is offline or repositories are unreachable. The script keeps going. Run those steps later. |
| "pam_tally2 not found" | Expected on newer images. Set up `pam_faillock` by hand if lockout is required. |
| SSH: "sshd_config failed validation" | The script restored the backup. Check `sudo sshd -t` for the reason. |
| Locked out of sudo | Revert the VM snapshot, or restore `/etc/pam.d/common-auth.backup` from a recovery shell |
| UFW conflict | Run `sudo ufw disable` then re-run the script |

---

## 12. Limitations

- Template lists (prohibited software, services) are generic and must be matched to each README.
- Audit policy commands use English category names.
- The scripts cover baseline settings. They will not catch image-specific vulnerabilities such as backdoors, hidden users, malicious scheduled tasks, insecure application configs or file permission traps.
- The settings follow common hardening guidance (CIS-style baselines and NIST recommendations) but are not a full implementation of any benchmark.
- The Windows scripts have not yet been run end to end by the author. Complete Section 6 before relying on them.

---

## Ethics

Scripts must be written by team members, used on practice images only, and used in line with all CyberPatriot rules. Do not share competition-specific material with other teams.

*Created by Moulik Suhag for the Georgia Governor's Honors Program computer science portfolio.*
