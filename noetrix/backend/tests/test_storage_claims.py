from pathlib import Path
import pytest


def test_no_localstorage_persistence_in_frontend():
    """Ensure candidate analyze and editor pages strictly use sessionStorage and do not write to localStorage."""
    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    analyze_page = frontend_dir / "app" / "candidate" / "analyze" / "page.tsx"
    editor_page = frontend_dir / "app" / "candidate" / "editor" / "page.tsx"

    assert analyze_page.exists(), "analyze/page.tsx must exist"
    assert editor_page.exists(), "editor/page.tsx must exist"

    analyze_text = analyze_page.read_text(encoding="utf-8")
    editor_text = editor_page.read_text(encoding="utf-8")

    # analyze page must not write noetrix keys to localStorage
    assert 'localStorage.setItem("noetrix_' not in analyze_text, (
        "localStorage.setItem('noetrix_...') found in analyze/page.tsx. Data must only live in sessionStorage."
    )

    # editor page must not read noetrix keys from localStorage fallback
    assert 'localStorage.getItem("noetrix_' not in editor_text, (
        "localStorage.getItem('noetrix_...') found in editor/page.tsx. Data must only live in sessionStorage."
    )
