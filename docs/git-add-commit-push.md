# Add, Commit and Push in Git

**Module:** Applied Robotics and AI Project - Assignment 1  
**Author:** Kenzo Ji

## 1. The four places your code lives

Git commands only make sense once you know that a file moves through four areas:

| Area | Where it is | What it holds |
|---|---|---|
| Working directory | Your project folder on disk | The files exactly as you are editing them right now |
| Staging area (index) | Inside the hidden `.git` folder | A list of changes you have picked to go into the next commit |
| Local repository | Inside the hidden `.git` folder | The full history of commits, stored on your own machine |
| Remote repository | GitHub | A shared copy of the history that others (and the lecturer) can see |

`git add`, `git commit` and `git push` each move changes one step along this path:

```
 Working directory --git add--> Staging area --git commit--> Local repo --git push--> GitHub
```

## 2. git add - choosing what goes into the next snapshot

`git add` copies the current state of a file from the working directory into the staging area. Nothing is saved to history yet. You are only telling Git "I want this change in my next commit".

```bash
git add src/flashcards/generator.py   # stage one file
git add .                             # stage every changed file in this folder
git status                            # green = staged, red = modified but not staged
```

Why have this step at all? It lets you split work into clean, separate commits. If I fixed a bug and also updated the README, I can add and commit the bug fix on its own first, then the README, so each commit does one thing.

If you edit a file again after adding it, the new edit is **not** staged. You have to `git add` it again.

**What `git add` will never pick up.** Files listed in `.gitignore` are invisible to `git add .` and `git status`. My project keeps its OpenAI API key in a `.env` file, and `.env` is in `.gitignore`. That way even `git add .` can't stage the key by accident, so it never reaches GitHub. The repository only contains `.env.example`, which shows the variable names with a fake value.

## 3. git commit - saving the snapshot to history

`git commit` takes everything in the staging area and records it permanently in the local repository as one commit. Each commit stores:

- a unique ID (a SHA-1 hash, e.g. `a3f9c1e`)
- the author's name and email
- the date and time
- a message describing the change
- a pointer to the previous commit, which is what forms the history

```bash
git commit -m "feat: generate flashcards with gpt-4o-mini"
git log --oneline              # view the history
```

A commit happens entirely on your own computer and needs no internet. Until you push, nobody else can see it. A good commit message says *what* changed and *why*, so the history reads like a project log. I use the prefixes `feat:`, `fix:`, `docs:` and `chore:`.

## 4. git push - sharing your commits with the remote

`git push` uploads the commits from your local repository that the remote doesn't have yet. After a push, the commits appear on GitHub, where they are backed up and visible to collaborators.

```bash
git push origin main                       # push the main branch
git push -u origin feature/card-generator   # first push of a new branch
```

Push needs a network connection and permission to write to the repository. If someone else pushed first, GitHub rejects the push. You then run `git pull` to bring in their commits, sort out any conflicts, and push again.

## 5. The differences side by side

| | `git add` | `git commit` | `git push` |
|---|---|---|---|
| Moves changes from | Working directory | Staging area | Local repository |
| Moves changes to | Staging area | Local repository | Remote (GitHub) |
| Creates history? | No | Yes, one new commit | No, it copies existing commits |
| Needs internet? | No | No | Yes |
| Visible to others? | No | No | Yes |
| Can be undone easily? | Yes (`git restore --staged <file>`) | Yes, locally (`git reset`, `git revert`) | Harder, others may already have it |

**Analogy.** Think of posting a parcel. `git add` is putting items in the box. `git commit` is sealing and labelling the box, so its contents are fixed. `git push` is handing the box to the courier so it reaches someone else. You can pack and seal several boxes (commits) before one trip to the courier (push).

## 6. The rest of the everyday cycle: Clone and Edit

- **Clone:** `git clone https://github.com/kennnyyyyyyy/ai-flashcard-maker.git` downloads the whole repository, including every commit, and sets GitHub up as the remote called `origin`. You normally do this once per machine.
- **Edit:** change files in any editor. Git notices automatically, and `git status` and `git diff` show what changed.

A full cycle, as shown in the video:

```bash
git clone https://github.com/kennnyyyyyyy/ai-flashcard-maker.git
cd ai-flashcard-maker
# edit README.md in VS Code
git status
git diff
git add README.md
git commit -m "docs: describe project goals"
git push origin main
```

## 7. Summary

`git add` chooses which changes to save, `git commit` saves them as a permanent snapshot on my machine, and `git push` sends those snapshots to GitHub. Keeping the three steps separate lets me make small, meaningful commits, work offline, and only share work once it is ready.
