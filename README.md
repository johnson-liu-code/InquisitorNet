## 🕵️‍♂️ InquisitorNet – overview & deployment (added by ChatGPT)

*Warhammer 40,000*–flavoured Reddit bot network.  Each “Inquisitor” account can post, reply, and audit subreddits for *heresy*.

### Tech stack
* **Python 3.11** – single file `inquisitor_net.py` (needs modularisation).
* **PRAW 7.7**, **OpenAI API**, **APScheduler** for scheduling posts.
* SQLite via `DatabaseManager` (simple ORM wrapper).

<!-- ### Quick start
```bash
export REDDIT_CLIENT_ID=...
export REDDIT_CLIENT_SECRET=...
export REDDIT_USERNAME_VERAX=...
export OPENAI_API_KEY=...
pip install -r requirements.txt
python inquisitor_net.py  # starts scheduler
``` -->

### Problems spotted
1. Credentials are read from *plain* env vars – supply an `.env.example`.  
2. Bot personalities / templates hard‑coded – move to `json/yaml`.  
3. No tests: skeleton shown in `directory_structure.txt` but not committed.  
4. Heresy keyword lists are simplistic; consider embedding similarity instead.  
5. Long file (800+ LOC) – split into modules (`bots.py`, `database.py`, `scheduler.py`).

### Suggested enhancements
* Add rate‑limit + exception back‑off for Reddit API.  
* Replace polling with Reddit stream listeners.  
* Expose CLI (`python -m inquisitornet …`).  
* Dockerfile for containerised deployment.

---

