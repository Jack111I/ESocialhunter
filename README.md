<img width="734" height="241" alt="Untitled-3 (12)" src="https://github.com/user-attachments/assets/72a420a5-ebce-48ca-ba3e-3f1c625c7cd6" />


# ESocialHunter — 300+ Platform OSINT Username Finder

ESocialHunter is a fast, local OSINT tool that checks a username across **300+ social, gaming, developer, marketplace, crypto, and forum platforms**.  
Runs fully on the user’s device with no limits, no API keys, and no hosting required.

---

## Features
- Scans 300+ platforms
- Parallel async requests (fast)
- JSON / CSV / TXT export
- Optional sensitive/dating checks
- 100% offline/local execution






## Installation
-- Clone the Repository

- git clone https://github.com/(httpsJack111I/ESocialhunter.git)
  
- cd ESocialHunter
- pip install -r requirements.txt


## Usage
python esocialhunter.py --username johndoe
python esocialhunter.py --username johndoe --json out.json
python esocialhunter.py --username johndoe --threads 50
python esocialhunter.py --username johndoe --include-sensitive


## Arguments
| Flag | Description |
|------|-------------|
| `--username` | Username to scan |
| `--threads` | Parallel requests |
| `--json` | Export JSON |
| `--csv` | Export CSV |
| `--txt` | Export TXT |
| `--include-sensitive` | Include dating/adult platforms |

## Requirements
Python 3.8+








