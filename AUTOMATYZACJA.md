# Automatyzacja — cotygodniowy raport prosto na Twój Google Drive

Cel: co **wtorek 9:00** raport generuje się sam i **automatycznie ląduje w udostępnionym folderze** na Twoim Google Drive (jako Google Doc). Twój udział po jednorazowym setupie: **zero**.

## Jak to działa (2 klocki)
1. **Harmonogram (trigger, cron `0 9 * * 2`)** — odpala świeżą sesję Claude Code, która robi research (ostatnie 7 dni), aktualizuje bazę konkurentów i generuje nowy raport + wersję czytelną (HTML).
2. **Upload** — ta sama sesja uruchamia `upload_to_drive.py`, który przez **Google Drive API** (konto serwisowe) wgrywa najnowszy raport do jednego, wskazanego folderu. Domyślnie konwertuje go do **Google Doc** (otwierasz i edytujesz wprost w Drive).

## Setup jednorazowy (ok. 15 min) — po Twojej stronie

### 1. Utwórz konto serwisowe w Google Cloud
1. Wejdź na **https://console.cloud.google.com** → utwórz projekt (np. „Szpieg Marketingowy").
2. **APIs & Services → Enable APIs → włącz „Google Drive API"**.
3. **APIs & Services → Credentials → Create credentials → Service account**. Nadaj nazwę (np. `raport-bot`).
4. Wejdź w utworzone konto serwisowe → zakładka **Keys → Add key → Create new key → JSON**. Pobierze się plik `.json`. To jest sekret — trzymaj bezpiecznie.
5. Zapisz adres e-mail konta serwisowego (wygląda tak: `raport-bot@twoj-projekt.iam.gserviceaccount.com`).

### 2. Udostępnij mu folder na Drive
1. Utwórz na Google Drive folder (np. „Raporty wywiadowcze").
2. Kliknij **Udostępnij** i dodaj adres konta serwisowego z kroku 1.5 jako **Edytor**.
3. Z adresu URL folderu skopiuj jego **ID** — to ciąg po `/folders/` w linku, np.
   `https://drive.google.com/drive/folders/`**`1AbCdEfGhIjKlMnOpQr`** → ID = `1AbCdEfGhIjKlMnOpQr`.

### 3. Ustaw zmienne środowiskowe w Claude Code
W **konfiguracji środowiska** (Environment → Environment Variables / Secrets):

| Zmienna | Wartość | Wymagana |
|---|---|---|
| `DRIVE_FOLDER_ID` | ID folderu z kroku 2.3 | ✅ tak |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **cała treść** pliku JSON z kroku 1.4 (wklej jako sekret) | ✅ tak |
| `DRIVE_AS_GOOGLE_DOC` | `1` = Google Doc (domyślnie) / `0` = surowy .html | nie |

> **Sekretów nie wklejaj do czatu** — wyłącznie do konfiguracji środowiska. Klucz konta serwisowego można w każdej chwili unieważnić w Google Cloud, a dostęp odebrać, usuwając konto z udostępnienia folderu.

## Test ręczny (gdy ustawisz zmienne)
```bash
python3 upload_to_drive.py --dry-run   # podgląd: co i do jakiego folderu (bez uploadu)
python3 upload_to_drive.py             # realny upload najnowszego raportu
```
Skrypt sam doinstaluje potrzebne biblioteki (`google-auth`, `requests`), jeśli ich brak.

## Zakres uprawnień (bezpieczeństwo)
- Skrypt używa scope `drive.file` — może operować **tylko na plikach, które sam utworzy** w udostępnionym folderze. Nie ma wglądu w resztę Twojego dysku.

## Awaryjnie / gdy coś nie zadziała
- Brak `DRIVE_FOLDER_ID` lub klucza → skrypt kończy się z jasnym komunikatem, a raport **i tak jest wygenerowany i zapisany w repo** (nic nie ginie).
- Błąd Drive API (np. konto serwisowe nie ma dostępu do folderu) → kod `3` + treść odpowiedzi Google w logu (najczęściej: dodaj konto serwisowe do udostępnienia folderu jako Edytor).

---
*Wysyłka mailem (`send_report.py`, Resend) pozostaje w repo jako opcjonalny, nieaktywny kanał zapasowy — obecny harmonogram używa wyłącznie Google Drive.*
