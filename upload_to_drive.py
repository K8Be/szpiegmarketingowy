#!/usr/bin/env python3
"""Wrzuca najnowszy tygodniowy raport do udostępnionego folderu na Google Drive.

Uwierzytelnianie: konto serwisowe (service account). Bot ma dostęp WYŁĄCZNIE
do folderu, który udostępnisz jego adresowi e-mail — nie widzi reszty dysku.

Domyślnie raport jest wgrywany jako natywny **Google Doc** (konwersja z HTML),
więc otwiera się i edytuje bezpośrednio w Drive. Ustaw DRIVE_AS_GOOGLE_DOC=0,
aby zostawić surowy plik .html.

Zmienne środowiskowe:
  DRIVE_FOLDER_ID              (wymagane)  — ID udostępnionego folderu (z URL-a folderu).
  GOOGLE_SERVICE_ACCOUNT_JSON  (wymagane*) — treść klucza JSON konta serwisowego.
  GOOGLE_SERVICE_ACCOUNT_FILE  (wymagane*) — ALTERNATYWNIE: ścieżka do pliku JSON.
                                (* podaj jedno z dwóch)
  DRIVE_AS_GOOGLE_DOC          (opcjonalne) — "1" (domyślnie) konwertuj do Google Doc; "0" = .html.

Użycie:
  python upload_to_drive.py            # wgrywa najnowszy raport
  python upload_to_drive.py --dry-run  # pokazuje, co poszłoby (bez uploadu, bez kluczy)
"""
import os
import re
import sys
import glob
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
UPLOAD_URL = ("https://www.googleapis.com/upload/drive/v3/files"
              "?uploadType=multipart&fields=id,name,webViewLink")


def _ensure_deps():
    try:
        import google.oauth2.service_account  # noqa: F401
        import google.auth.transport.requests  # noqa: F401
        import requests  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "google-auth>=2.0", "requests>=2.25"],
            check=True,
        )


def newest_report():
    """Najnowszy plik e-mail HTML (czytelna wersja); fallback: najnowszy raport .md."""
    html = sorted(glob.glob(os.path.join(BASE_DIR, "raporty", "*-email-do-marketingu.html")))
    if html:
        return html[-1]
    md = sorted(glob.glob(os.path.join(BASE_DIR, "raporty", "*-raport-wywiadowczy.md")))
    return md[-1] if md else None


def main():
    dry = "--dry-run" in sys.argv
    folder_id = os.environ.get("DRIVE_FOLDER_ID")
    as_doc = os.environ.get("DRIVE_AS_GOOGLE_DOC", "1") != "0"

    path = newest_report()
    if not path:
        print("BŁĄD: nie znaleziono raportu w raporty/ (*.html lub *.md)", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        content = f.read()

    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    date = m.group(1) if m else "raport"
    is_html = path.endswith(".html")
    src_mime = "text/html" if is_html else "text/markdown"
    title = f"Raport wywiadowczy — Pracownia Gier — {date}"
    metadata = {"name": title if as_doc else os.path.basename(path), "parents": [folder_id] if folder_id else []}
    if as_doc:
        metadata["mimeType"] = GOOGLE_DOC_MIME
    target = "Google Doc" if as_doc else "surowy plik"

    if dry:
        print(f"[dry-run] plik źródłowy = {path} ({len(content)} znaków, {src_mime})")
        print(f"[dry-run] nazwa w Drive = {metadata['name']}  ->  {target}")
        print(f"[dry-run] folder ID    = {folder_id or '(BRAK — ustaw DRIVE_FOLDER_ID)'}")
        return

    if not folder_id:
        print("BŁĄD: brak DRIVE_FOLDER_ID — raport NIE został wgrany (jest zapisany w repo).", file=sys.stderr)
        sys.exit(2)

    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    key_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not raw and not key_file:
        print("BŁĄD: brak GOOGLE_SERVICE_ACCOUNT_JSON / _FILE — raport NIE został wgrany.", file=sys.stderr)
        sys.exit(2)

    _ensure_deps()
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request, AuthorizedSession

    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)

    session = AuthorizedSession(creds)
    boundary = "===============szpieg-boundary=="
    body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {src_mime}; charset=UTF-8\r\n\r\n"
        f"{content}\r\n"
        f"--{boundary}--"
    ).encode("utf-8")

    r = session.post(
        UPLOAD_URL,
        data=body,
        headers={"Content-Type": f"multipart/related; boundary={boundary}"},
        timeout=60,
    )
    if r.status_code >= 300:
        print(f"BŁĄD Drive API {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(3)
    info = r.json()
    print(f"OK: wgrano '{info.get('name')}' do folderu ({target})")
    print(f"    link: {info.get('webViewLink')}")


if __name__ == "__main__":
    main()
