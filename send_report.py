#!/usr/bin/env python3
"""Wysyła raport mailem przez Resend API (bez zależności poza opcjonalnym 'markdown').

Użycie:
  python3 send_report.py                 # wysyła najnowszy raport HTML (raporty/*-email-do-marketingu.html)
  python3 send_report.py raporty/x.md    # wysyła wskazany plik (.md konwertowany do HTML, .html bez zmian)
  python3 send_report.py --dry-run [plik]

Zmienne środowiskowe:
  RESEND_API_KEY  (wymagane)  — klucz API z https://resend.com
  REPORT_TO       (opcjonalne) — odbiorca; domyślnie marketing@pracowniagier.com
  REPORT_FROM     (opcjonalne) — nadawca; domyślnie onboarding@resend.dev (tryb testowy Resend)
"""
import os
import re
import sys
import glob
import json
import datetime
import subprocess
import urllib.request
import urllib.error

RESEND_ENDPOINT = "https://api.resend.com/emails"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def newest_email_html():
    files = sorted(glob.glob(os.path.join(BASE_DIR, "raporty", "*-email-do-marketingu.html")))
    return files[-1] if files else None


def md_to_html(md_text):
    """Konwersja Markdown -> HTML. Próbuje biblioteki 'markdown', w razie braku – prosty fallback."""
    try:
        import markdown  # noqa
    except ImportError:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "markdown"], check=True)
            import markdown  # noqa
        except Exception:
            markdown = None
    if markdown:
        body = markdown.markdown(md_text, extensions=["extra", "sane_lists", "nl2br"])
    else:
        # Fallback: zachowaj układ w bloku preformatowanym (czytelne, bez utraty treści).
        import html as _html
        body = "<pre style='white-space:pre-wrap;font-family:inherit'>" + _html.escape(md_text) + "</pre>"
    return (
        "<div style=\"max-width:680px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,Arial,"
        "sans-serif;color:#1a1a1a;line-height:1.5;font-size:15px\">" + body + "</div>"
    )


def load_content(path):
    """Zwraca (html, data_str) dla wskazanego pliku lub najnowszego raportu."""
    if not path:
        path = newest_email_html()
        if not path:
            print("BŁĄD: nie znaleziono raportu (raporty/*-email-do-marketingu.html)", file=sys.stderr)
            sys.exit(1)
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    if not os.path.exists(path):
        print(f"BŁĄD: plik nie istnieje: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    html = md_to_html(raw) if path.endswith(".md") else raw
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    date = m.group(1) if m else datetime.date.today().isoformat()
    return html, date


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    path = args[0] if args else None

    api_key = os.environ.get("RESEND_API_KEY")
    to_addr = os.environ.get("REPORT_TO", "marketing@pracowniagier.com")
    from_addr = os.environ.get("REPORT_FROM", "Szpieg Marketingowy <onboarding@resend.dev>")

    html, date = load_content(path)
    subject = f"\U0001F575️ Raport wywiadowczy — konkurencja + trendy L&D | {date}"
    payload = {"from": from_addr, "to": [to_addr], "subject": subject, "html": html}

    if dry:
        print(f"[dry-run] from={from_addr}\n[dry-run] to={to_addr}\n[dry-run] subject={subject}")
        print(f"[dry-run] plik={path or '(najnowszy HTML)'} ({len(html)} znaków HTML)")
        return

    if not api_key:
        print("BŁĄD: brak RESEND_API_KEY — mail NIE został wysłany.", file=sys.stderr)
        sys.exit(2)

    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Cloudflare przed Resend blokuje domyslny UA Pythona (403 error code 1010).
            "User-Agent": "Mozilla/5.0 (compatible; PracowniaGier-Raport/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
        print(f"OK: wysłano na {to_addr} (id={resp.get('id')})")
    except urllib.error.HTTPError as e:
        print(f"BŁĄD HTTP {e.code}: {e.read().decode(errors='replace')}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:  # noqa: BLE001
        print(f"BŁĄD wysyłki: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
