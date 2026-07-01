# Git & GitHub Cheatsheet

Welcome to the Git guide! This document explains the most important and frequently used Git commands. It is designed to help anyone learn how to configure Git, manage branches, fetch/pull changes, push changes, and successfully create a Pull Request (PR).

---

## Table of Contents
1. [Git Configuration & Setup](#1-git-configuration--setup)
2. [Starting or Cloning a Repository](#2-starting-or-cloning-a-repository)
3. [The Daily Code-Stage-Commit Cycle](#3-the-daily-code-stage-commit-cycle)
4. [Branching (Working on Features)](#4-branching-working-on-features)
5. [Syncing Changes (Pull & Push)](#5-syncing-changes-pull--push)
6. [Step-by-Step Guide: How to Open a Pull Request (PR)](#6-step-by-step-guide-how-to-open-a-pull-request-pr)
7. [Undoing & Resetting Changes](#7-undoing--resetting-changes)
8. [Useful Utility Commands](#8-useful-utility-commands)

---

## 1. Git Configuration & Setup

Before making commits, you need to configure your identity so Git knows who authored the changes.

### Configure Username
```bash
git config --global user.name "Your Name"
```
* **Explanation:** Sets the name that will be attached to your commits globally on your machine.

### Configure Email
```bash
git config --global user.email "your.email@example.com"
```
* **Explanation:** Sets the email address that will be associated with your commits. It is recommended to use the email associated with your GitHub/GitLab account.

### Check Configuration
```bash
git config --list
```
* **Explanation:** Displays all current Git configurations (name, email, default branch, etc.).

---

## 2. Starting or Cloning a Repository

### Initialize a New Repository
```bash
git init
```
* **Explanation:** Turns the current folder into a new Git repository, creating a hidden `.git` folder inside it.

### Clone an Existing Repository
```bash
git clone <repository-url>
```
* **Explanation:** Downloads an existing repository from a remote hosting service (like GitHub) to your local machine.

---

## 3. The Daily Code-Stage-Commit Cycle

Working with Git follows a simple three-step rhythm: **Modify files** $\rightarrow$ **Stage changes** $\rightarrow$ **Commit them**.

```
   [ Working Directory ]  -- (git add) -->  [ Staging Area ]  -- (git commit) -->  [ Git History (.git) ]
```

### Check Repository Status
```bash
git status
```
* **Explanation:** Shows which files have been modified, created, or deleted, and whether they are currently staged (ready to commit) or unstaged.

### Stage Changes
```bash
# Stage a specific file
git add filename.txt

# Stage all changes in the current directory and subdirectories
git add .
```
* **Explanation:** Prepares files for a commit by adding them to the staging area.

### Commit Changes
```bash
git commit -m "Commit message describing the changes"
```
* **Explanation:** Saves a snapshot of the staged files to your local repository history. Write clear and concise messages (e.g., `"feat: add search bar to dashboard"`).

### View Commit History
```bash
# View full history
git log

# View a clean, one-line summary of history
git log --oneline
```
* **Explanation:** Displays the chronological list of commits in the current branch.

### Compare Changes
```bash
# Compare unstaged modifications to the last commit
git diff

# Compare staged changes to the last commit
git diff --staged
```
* **Explanation:** Shows the line-by-line differences in your files.

---

## 4. Branching (Working on Features)

Branches allow you to work on new features or bug fixes safely without affecting the stable `main` or `develop` code.

### List Branches
```bash
git branch
```
* **Explanation:** Lists all local branches in the repository. The active branch has an asterisk (`*`) next to it.

### Create a New Branch
```bash
git branch <branch-name>
```
* **Explanation:** Creates a new branch pointing to your current commit but does *not* switch you to it.

### Switch to a Branch
```bash
# Older command:
git checkout <branch-name>

# Modern recommended command:
git switch <branch-name>
```
* **Explanation:** Switches your workspace to the specified branch.

### Create and Switch to a New Branch in One Step
```bash
# Older command:
git checkout -b <branch-name>

# Modern recommended command:
git switch -c <branch-name>
```
* **Explanation:** Creates a new branch and immediately switches you to it.

### Merge Changes
```bash
git merge <branch-name>
```
* **Explanation:** Merges the history of the specified branch into your *currently active* branch.
* **Tip:** Always switch to the target branch (e.g., `main`) before running `git merge`.

### Delete a Local Branch
```bash
# Delete branch (only if it has been merged)
git branch -d <branch-name>

# Force delete branch (even if it has unmerged changes)
git branch -D <branch-name>
```
* **Explanation:** Deletes the branch locally to keep the repository clean.

---

## 5. Syncing Changes (Pull & Push)

Remote repositories (hosted on platforms like GitHub) are referenced by names (commonly `origin`).

### View Remotes
```bash
git remote -v
```
* **Explanation:** Shows the remote repository URLs linked to your local repository.

### Fetch Remote Changes
```bash
git fetch
```
* **Explanation:** Downloads the latest history and references from the remote repository, but does *not* modify your current working files.

### Pull Changes (Fetch + Merge)
```bash
git pull origin <branch-name>
```
* **Explanation:** Downloads the latest changes from the specified remote branch and automatically merges them into your current branch.

### Push Changes
```bash
# Push branch for the first time (sets upstream tracking)
git push -u origin <branch-name>

# Push subsequent changes
git push
```
* **Explanation:** Uploads your local commits to the remote repository. The `-u` (or `--set-upstream`) flag links your local branch to the remote branch.

---

## 6. Step-by-Step Guide: How to Open a Pull Request (PR)

A Pull Request is a way to propose changes from your feature branch to a shared main branch (e.g., `develop` or `main`), allowing team members to review and discuss changes before they are merged.

Follow this standard workflow:

### Step 1: Ensure Your Main/Develop Branch is Up-to-Date
Before starting work, make sure you have the latest code.
```bash
git checkout develop
git pull origin develop
```

### Step 2: Create a Feature Branch
Create a descriptive branch for your task.
```bash
git checkout -b feature/my-cool-feature
```

### Step 3: Write Code, Stage, and Commit
Build your changes, then stage and commit them.
```bash
# Check status to see what changed
git status

# Stage the files
git add .

# Save the commit locally
git commit -m "feat: add user profile picture upload"
```

### Step 4: Pull Latest Remote Changes to Avoid Conflicts
Before pushing, ensure no one else committed changes to the target branch that would conflict with yours.
```bash
git pull origin develop
```
*If conflicts arise, Git will prompt you to resolve them in your editor. Save, add, and commit the resolved files.*

### Step 5: Push Your Branch to GitHub
```bash
git push -u origin feature/my-cool-feature
```

### Step 6: Open the Pull Request on GitHub
1. Go to the repository page on GitHub in your web browser.
2. You will see a banner saying: **"Your branch was recently pushed. Compare & pull request."**
3. Click the green **"Compare & pull request"** button.
4. Select the target branch:
   - **base:** (e.g., `develop` or `main`) — the branch you want to merge *into*.
   - **compare:** `feature/my-cool-feature` — your branch.
5. Write a title and a description explaining the changes.
6. Click **"Create pull request"**.

---

## 7. Undoing & Resetting Changes

### Discard Unstaged Changes in a File
```bash
git restore <filename>
```
* **Explanation:** Discards local uncommitted modifications in the specified file, reverting it to the last committed state.

### Unstage a File (Keep the edits)
```bash
git restore --staged <filename>
```
* **Explanation:** Removes the file from the staging area, but preserves your changes in the working directory.

### Revert a Public Commit
```bash
git revert <commit-hash>
```
* **Explanation:** Creates a new commit that does the exact opposite of the specified commit. This is the safest way to undo changes that have already been pushed to a remote repository.

### Reset Local Branch to a Previous State (Dangerous!)
```bash
# Soft reset: keeps your changed files in the staging area
git reset --soft <commit-hash>

# Hard reset: discards ALL changes in the working tree and staging area
git reset --hard <commit-hash>
```
* **Explanation:** Moves your current branch pointer backward to a specific commit. 
* **Warning:** `git reset --hard` will permanently delete your uncommitted work and any commits after the specified hash. Use with caution!

---

## 8. Useful Utility Commands

### Temporarily Save Work (Stashing)
If you need to switch branches but aren't ready to commit your current work, stash it:
```bash
# Save current work to a temporary stash
git stash

# Switch to another branch, do work, switch back, and then re-apply:
git stash pop
```
* **Explanation:** `git stash` saves your modified workspace and resets it to match the clean HEAD. `git stash pop` restores the stashed files.

### Clean Untracked Files
```bash
git clean -fd
```
* **Explanation:** Deletes untracked files (`-f`) and untracked directories (`-d`) from your local directory.
