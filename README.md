# AI Flashcard Maker

Applied Robotics and AI Project, University of Hertfordshire (PSB Academy)
Kenzo Ji

A small command-line tool that turns lecture notes into study flashcards. You give it a
`.txt`, `.md` or `.pdf` file, it asks GPT-4o-mini to pull out the key facts as questions
and answers, and saves them as a CSV you can import into Anki or Quizlet.

Project board: https://trello.com/b/lzUqMxdc

## Example

```
> python src/main.py examples/sample-notes.txt --max-cards 3
Reading examples/sample-notes.txt and asking gpt-4o-mini for up to 3 cards...

1. How does an ultrasonic sensor measure distance?
   It times how long a sound pulse takes to echo back, then halves the distance.

2. What does the integral term of a PID controller do?
   It removes steady error that builds up over time.

3. Why is A* guaranteed to find the shortest path?
   Because its heuristic never overestimates the remaining distance.

Saved 3 cards to examples/sample-notes-flashcards.csv and examples/sample-notes-flashcards.md
```

## How it works

1. `reader.py` reads the document. PDFs are read page by page.
2. Long text is split into chunks between paragraphs, so each request stays a sensible size.
3. `generator.py` sends each chunk to GPT-4o-mini and asks for the cards back as JSON.
4. Incomplete cards are skipped and duplicate questions are removed.
5. `exporter.py` saves the cards as CSV and Markdown.

## Setup

```
git clone https://github.com/kennnyyyyyyy/ai-flashcard-maker.git
cd ai-flashcard-maker
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and put your OpenAI API key in place of `sk-your-key-here`. Then:

```
python -m pytest                              # run the tests (no API key needed)
python src/main.py examples/sample-notes.txt  # make flashcards
```

Options: `--max-cards N` sets how many cards to make (default 10), and `--out NAME`
sets the output file name.

## Keeping the API key safe

The key lives only in `.env` on my laptop. `.env` is listed in `.gitignore`, so Git never
tracks it and it can't be pushed to GitHub by accident. The repo has `.env.example`
instead, which shows the setting names with a fake value. The tests use a fake OpenAI
client, so GitHub Actions can run them without a key.

## Project layout

```
src/main.py                    command-line tool
src/flashcards/config.py       loads the API key and model from .env
src/flashcards/reader.py       reads .txt, .md and .pdf files
src/flashcards/generator.py    asks GPT-4o-mini for flashcards
src/flashcards/exporter.py     saves CSV and Markdown
tests/                         unit tests
docs/git-add-commit-push.md    notes on add, commit and push
docs/assignment-1-report.md    Assignment 1 report with screenshots (also as PDF)
.github/workflows/             tests and Trello sync on every pull request
```

## Git workflow

Every change goes through the same steps:

```
edit files  --git add-->  staging area  --git commit-->  local history  --git push-->  GitHub
```

- `git add` chooses which changes go into the next commit.
- `git commit` saves those changes as a snapshot on my computer, with a message.
- `git push` uploads my commits to GitHub so they are backed up and visible.
- `git clone` downloads the whole repository once; `git pull` fetches new commits.

More detail is in [docs/git-add-commit-push.md](docs/git-add-commit-push.md).

The full Assignment 1 report, with screenshots of every step, is in
[docs/assignment-1-report.md](docs/assignment-1-report.md) ([PDF](docs/Assignment-1-Report.pdf)).

## Branching strategy

- `main` only holds working, tested code. It is protected, so changes can only get in
  through a pull request with passing tests.
- Each feature gets its own branch, named after its Trello card and GitHub issue,
  for example `feature/card-generator`.
- I commit in small steps, push the branch, and open a pull request. The pull request
  says which issue it closes and links its Trello card.
- GitHub Actions runs the tests. Once they pass I merge the pull request and delete
  the branch.

```
git switch main
git pull
git switch -c feature/card-generator
# edit, git add, git commit
git push -u origin feature/card-generator
# open a pull request, wait for the tests, merge, delete the branch
```

Commit messages start with the type of change, for example `feat: add PDF support`,
`fix: skip empty answers`, `test: cover duplicate removal` or `docs: update README`.

## Planning with Trello

The board has six lists: Backlog, To Do, In Progress (limit of 2 cards), Review / PR,
Done and Retrospective. Every card has a due date, a checklist and the branch it uses.

Trello and GitHub are linked in two ways. The GitHub Power-Up attaches each pull request
to its card. A GitHub Action also moves the card to Review / PR when a pull request opens,
and to Done when it is merged, and leaves a comment with the link.

## Next steps

- Export straight to an Anki deck
- A quiz mode with spaced repetition
- Show token usage and cost per run
- A simple web page for uploading files

## License

MIT, see [LICENSE](LICENSE).
