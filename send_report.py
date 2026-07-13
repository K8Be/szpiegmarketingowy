#!/usr/bin/env python3
"""Wysyła najnowszy tygodniowy raport (HTML) na skrzynkę marketingu przez Resend API.

Nie wymaga zależności zewnętrznych (tylko biblioteka standardowa Pythona).

Zmienne środowiskowe:
  RESEND_API_KEY  (wymagane)  — klucz API z https://resend.com
  REPORT_TO       (opcjonalne) — adres odbiorcy; domyślnie marketing@pracowniagier.com
  REPORT_FROM     (opcjonalne) — nadawca; domyślnie testowy onboarding@resend.dev
                                 Do produkcji ustaw np. "Szpieg Marketingowy <raport@pracowniagier.com>"
                                 (domena musi być zweryfikowana w Resend).

Użycie:
  python send_report.py            # wysyła najnowszy raport
  python send_report.py --dry-run  # tylko pokazuje, co poszłoby (bez wysyłki, bez klucza)
"""
import os
import re
import sys
import glob
import json
import datetime
import urllib.request
import urllib.error

RESEND_ENDPOINT = "https://api.resend.com/emails"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def newest_email_html():
    files = sorted(glob.glob(os.path.join(BASE_DIR, "raporty", "*-email-do-marketingu.html")))
    return files[-1] if files else None


def main():
    dry = "--dry-run" in sys.argv
    api_key = os.environ.get("RESEND_API_KEY")
    to_addr = os.environ.get("REPORT_TO", "marketing@pracowniagier.com")
    from_addr = os.environ.get("REPORT_FROM", "Szpieg Marketingowy <onboarding@resend.dev>")

    path = newest_email_html()
    if not path:
        print("BŁĄD: nie znaleziono pliku raportu (raporty/*-email-do-marketingu.html)", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        html = f.read()

    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    date = m.group(1) if m else datetime.date.today().isoformat()
    subject = f"\U0001F575️ Raport wywiadowczy — konkurencja + trendy L&D | {date}"

    payload = {"from": from_addr, "to": [to_addr], "subject": subject, "html": html}

    if dry:
        print(f"[dry-run] from   = {from_addr}")
        print(f"[dry-run] to     = {to_addr}")
        print(f"[dry-run] subject= {subject}")
        print(f"[dry-run] plik   = {path} ({len(html)} znaków HTML)")
        return

    if not api_key:
        print("BŁĄD: brak zmiennej środowiskowej RESEND_API_KEY — mail NIE został wysłany.", file=sys.stderr)
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
