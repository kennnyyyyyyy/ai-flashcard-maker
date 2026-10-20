"""Start the web page.

Usage:
    python src/web.py
then open http://127.0.0.1:5000 in your browser.
"""

from flashcards.web import create_app

if __name__ == "__main__":
    print("Flashcard maker running at http://127.0.0.1:5000  (Ctrl+C to stop)")
    create_app().run(host="127.0.0.1", port=5000)
