# Git Commands to Push to GitHub

## Step-by-Step Commands

### 1. Navigate to Project Directory
```bash
cd "/Users/sujithdugyala/Desktop/data 236/group project"
```

### 2. Check Current Status
```bash
git status
```

### 3. Add .gitignore (if not already added)
```bash
git add .gitignore
git commit -m "Add .gitignore file"
```

### 4. Add All Project Files
```bash
# Add backend services
git add backend/
git add ai_service/
git add client/
git add database/
git add docker/
git add data/
git add tests/
git add docker-compose.yml
git add requirements.txt
git add README.md
git add test_csv_ingestion.py
```

### 5. Check What Will Be Committed
```bash
git status
```

### 6. Commit All Changes
```bash
git commit -m "Complete Team 1 implementation: User Service, Admin Service, AI Service, Frontend, CSV Ingestion"
```

### 7. Push to GitHub
```bash
git push origin main
```

---

## Alternative: Add Everything at Once (Faster)

If you want to add everything in one go:

```bash
cd "/Users/sujithdugyala/Desktop/data 236/group project"

# Add all files in current directory (respects .gitignore)
git add .

# Check status
git status

# Commit
git commit -m "Complete Team 1 implementation: User Service, Admin Service, AI Service, Frontend, CSV Ingestion"

# Push
git push origin main
```

---

## If You Need to Create a New Branch

```bash
# Create and switch to new branch
git checkout -b team1-implementation

# Add files
git add .

# Commit
git commit -m "Complete Team 1 implementation"

# Push to new branch
git push origin team1-implementation
```

---

## If You Get Authentication Errors

If GitHub asks for authentication:

```bash
# Option 1: Use Personal Access Token
# When prompted for password, use your GitHub Personal Access Token

# Option 2: Update remote URL with token
git remote set-url origin https://YOUR_TOKEN@github.com/sujith2511/airbnb.git

# Option 3: Use SSH (if you have SSH keys set up)
git remote set-url origin git@github.com:sujith2511/airbnb.git
```

---

## Quick One-Liner (All Steps)

```bash
cd "/Users/sujithdugyala/Desktop/data 236/group project" && git add . && git commit -m "Complete Team 1 implementation: User Service, Admin Service, AI Service, Frontend, CSV Ingestion" && git push origin main
```

---

## Verify After Push

```bash
# Check remote status
git remote -v

# Check last commit
git log -1

# Verify files are pushed
git ls-remote origin main
```

