# GEO Audit Environment - Timeline & Coordination

## Deadline: April 8th, 2026

**You have approximately 24 hours.**

---

## Team Split

```
HIJAK (Technical Lead)
├── Environment coding
├── Docker setup
├── Deployment to HF
├── inference.py
├── Data conversion (Sheet → JSON)
├── Testing & debugging

HARI (Data Lead)
├── Find 60 webpages
├── Analyze each page
├── Label issues
├── Fill Google Sheet
├── Quality check
```

---

## Hour-by-Hour Timeline

### PHASE 1: SETUP (Hours 0-2)

**HIJAK:**
```
Hour 0-1:
├── Create project folder
├── Set up virtual environment
├── Install openenv-core
├── Run openenv init
├── Create folder structure

Hour 1-2:
├── Create models.py
├── Create basic environment.py
├── Test server starts
├── Share this doc with Hari
```

**HARI:**
```
Hour 0-2:
├── Read the Data Collection Guide
├── Create Google Sheet with template
├── Understand the issue types
├── Start finding pages
```

---

### PHASE 2: PARALLEL WORK (Hours 2-8)

**HIJAK:**
```
Hour 2-4:
├── Complete environment.py
├── Create grader.py
├── Test with dummy data
├── Verify step(), reset(), state() work

Hour 4-6:
├── Create inference.py
├── Test inference locally
├── Fix any bugs

Hour 6-8:
├── Create Dockerfile
├── Build and test Docker
├── Fix container issues
```

**HARI:**
```
Hour 2-4:
├── TASK 1: Find and label 10 easy pages
├── Add to Google Sheet

Hour 4-6:
├── TASK 1: Complete remaining 10 easy pages
├── Start TASK 2: Find 10 medium pages

Hour 6-8:
├── TASK 2: Complete remaining 10 medium pages
├── Start TASK 3: Find 5 hard pages
```

---

### PHASE 3: DATA INTEGRATION (Hours 8-12)

**HIJAK:**
```
Hour 8-10:
├── Get first batch from Hari (Task 1)
├── Convert to JSON
├── Test with real data
├── Debug any issues

Hour 10-12:
├── Get Task 2 data from Hari
├── Convert and test
├── Run full inference test
├── Fix reward calculation if needed
```

**HARI:**
```
Hour 8-10:
├── TASK 3: Complete remaining 15 hard pages
├── Review all entries for errors

Hour 10-12:
├── Final quality check
├── Export all 3 sheets as CSV
├── Send to Hijak
├── Start helping with testing
```

---

### PHASE 4: DEPLOYMENT (Hours 12-18)

**HIJAK:**
```
Hour 12-14:
├── Get final data from Hari
├── Convert all to JSON
├── Final local test
├── Fix any last bugs

Hour 14-16:
├── Push to Hugging Face Spaces
├── Wait for build
├── Test deployed version
├── Debug deployment issues

Hour 16-18:
├── Run inference against deployed env
├── Verify logs match format
├── Check rewards are 0.0-1.0
├── Check rewards vary
```

**HARI:**
```
Hour 12-18:
├── Help test the deployed version
├── Try the /web interface
├── Report any issues to Hijak
├── Help write README sections
```

---

### PHASE 5: POLISH & SUBMIT (Hours 18-24)

**BOTH:**
```
Hour 18-20:
├── Run openenv validate
├── Fix any validation errors
├── Document baseline scores
├── Complete README

Hour 20-22:
├── Final end-to-end test
├── Record baseline scores for each task
├── Make sure inference completes in < 20 min

Hour 22-24:
├── Final check of submission requirements
├── Submit to hackathon
├── Celebrate! 🎉
```

---

## Communication Checkpoints

```
CHECKPOINT 1 (Hour 2):
├── Hijak: "Server running, here's the project structure"
├── Hari: "Got it, starting data collection"

CHECKPOINT 2 (Hour 4):
├── Hari: "10 easy pages done, here's the sheet link"
├── Hijak: "Great, I'll test with those"

CHECKPOINT 3 (Hour 8):
├── Hari: "Task 1 complete (20 pages), Task 2 halfway done"
├── Hijak: "Environment working, converting your data"

CHECKPOINT 4 (Hour 12):
├── Hari: "All 60 pages labeled and sent"
├── Hijak: "Starting deployment"

CHECKPOINT 5 (Hour 16):
├── Hijak: "Deployed! Test here: [HF Space URL]"
├── Hari: "Testing now"

CHECKPOINT 6 (Hour 20):
├── Both: "Final testing, preparing submission"

CHECKPOINT 7 (Hour 23):
├── Both: "Submitted! ✅"
```

---

## Quick Commands Reference

### For Hijak

```bash
# Setup
cd ~/geo-audit-env
source venv/bin/activate

# Local server
uvicorn server.app:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -d '{"task_difficulty":"easy"}'

# Docker
docker build -t geo-audit-env .
docker run -p 8000:8000 geo-audit-env

# Deploy
openenv push --repo-id YOUR_USERNAME/geo-audit-env

# Validate
openenv validate

# Run inference
export HF_TOKEN="hf_xxxxx"
export ENV_URL="http://localhost:8000"
python inference.py
```

### For Hari

```
# Schema validator
https://validator.schema.org/

# Word counter
https://wordcounter.net/

# View page source
Right-click → View Page Source

# Search in source
Cmd+F (Mac) or Ctrl+F (Windows)
├── Search: <title>
├── Search: <meta name="description"
├── Search: application/ld+json
```

---

## Submission Checklist

### Technical Requirements

```
☐ HF Space deploys and responds
☐ /health returns 200
☐ /reset works for all 3 tasks
☐ /step processes actions
☐ Docker builds successfully
☐ inference.py completes without error
☐ Logs show [START], [STEP], [END] format
☐ Rewards between 0.0 and 1.0
☐ Rewards vary (not same every time)
☐ Runtime < 20 minutes
☐ Works on 2 vCPU / 8GB RAM
```

### Content Requirements

```
☐ 3 tasks defined (easy, medium, hard)
☐ Each task has programmatic grader
☐ Graders return scores 0.0-1.0
☐ Task difficulty progression (easy → hard)
☐ 20 pages per task (60 total)
☐ Real-world task (not a toy)
```

### Documentation Requirements

```
☐ README.md complete
├── Environment description
├── Action space documented
├── Observation space documented
├── Task descriptions
├── Setup instructions
├── Baseline scores
☐ openenv.yaml complete
☐ All files in correct locations
```

---

## Emergency Contacts

If something goes wrong:

```
HIJAK STUCK ON CODE:
├── Check OpenEnv docs: https://meta-pytorch.org/OpenEnv/
├── Check existing envs: https://huggingface.co/openenv
├── Ask in Discord/Slack

HARI STUCK ON DATA:
├── Ask Hijak for clarification
├── Take best guess and note it
├── Move on, don't get blocked

DEPLOYMENT FAILING:
├── Check Dockerfile syntax
├── Check pyproject.toml
├── Check HF Space logs
├── Try rebuilding from scratch

RUNNING OUT OF TIME:
├── Reduce to 10 pages per task (30 total)
├── Skip Task 3 (hard) if needed
├── Submit whatever works
```

---

## Success Metrics

After submission, you should have:

```
BASELINE SCORES (Example):
├── Easy task: ~0.7-0.9 average reward
├── Medium task: ~0.4-0.7 average reward
├── Hard task: ~0.2-0.5 average reward

These show:
├── Environment works ✅
├── Difficulty progression ✅
├── Rewards are meaningful ✅
```

---

## Final Notes

1. **Don't perfectionism.** Done > Perfect.
2. **Communicate frequently.** Don't go silent.
3. **Test early, test often.** Find bugs before deadline.
4. **Submit something.** A working submission beats no submission.

Good luck! 🚀
