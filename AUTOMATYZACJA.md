# Automatyzacja — cotygodniowy raport prosto na Twój Google Drive

Cel: co **wtorek 9:00** raport generuje się sam i **automatycznie ląduje w udostępnionym folderze** na Twoim Google Drive (jako Google Doc). Twój udział po jednorazowym setupie: **zero**.

## Jak to działa (2 klocki)
1. **Harmonogram (trigger, cron `0 9 * * 2`)** — odpala świeżą sesję Claude Code, która robi research (ostatnie 7 dni), aktualizuje bazę konkurentów i generuje nowy raport + wersję czytelną (HTML).
2. **Upload** — ta sama sesja uruchamia `upload_to_drive.py`, który przez **Google Drive API** (konto serwisowe) wgrywa najnowszy raport do jednego, wskazanego folderu. Domyślnie konwertuje go do **Google Doc** (otwierasz i edytujesz wprost w Drive).

## Setup jednorazowy (ok. 15 min) — po Twojej stronie
> Nazwy menu podane wg **polskiego** panelu Google Cloud (w nawiasach oryginał EN).

### 1. Utwórz projekt i włącz Google Drive API
1. Wejdź na **https://console.cloud.google.com**.
2. U góry, przy logo, kliknij selektor projektu → **Nowy projekt** → nazwa (np. „Szpieg Marketingowy") → **Utwórz**. Poczekaj i przełącz się na ten projekt.
3. Menu ☰ (lewy górny róg) → **Interfejsy API i usługi** (*APIs & Services*) → **Biblioteka** (*Library*).
4. Wpisz **Google Drive API** → wejdź → **Włącz** (*Enable*).

### 2. Utwórz konto usługi (service account) — OMIJAJĄC ekran zgody OAuth
> ⚠️ **Tu się zwykle blokujesz.** Na stronie „Dane logowania" Google namawia na **„Skonfiguruj ekran zgody OAuth"** (*Configure consent screen*). **NIE klikaj tego** — dla konta usługi jest zbędne. Idź dokładnie tak:

1. Menu ☰ → **Interfejsy API i usługi** → **Dane logowania** (*Credentials* — tak Google tłumaczy „Credentials"!).
2. U góry kliknij **+ Utwórz dane logowania** (*+ Create credentials*) → z listy wybierz **Konto usługi** (*Service account*).
   - *(Alternatywnie, jeśli nie widzisz tej opcji: menu ☰ → **Uprawnienia (IAM) i administracja** → **Konta usługi** → **+ Utwórz konto usługi**.)*
3. **Nazwa konta usługi** (*Service account name*): np. `raport-bot` → **Utwórz i kontynuuj** (*Create and continue*).
4. Krok „Przyznaj temu kontu dostęp…" (*Grant access* — role) → **pomiń**, kliknij **Dalej/Kontynuuj**, a potem **Gotowe** (*Done*). Rola nie jest tu potrzebna — dostęp nadasz przez udostępnienie folderu.

### 3. Wygeneruj klucz JSON
1. Na liście **Konta usługi** kliknij utworzone `raport-bot@...`.
2. Zakładka **Klucze** (*Keys*) → **Dodaj klucz** (*Add key*) → **Utwórz nowy klucz** (*Create new key*).
3. Typ **JSON** → **Utwórz**. Pobierze się plik `.json` — **to jest sekret**, trzymaj bezpiecznie.
4. Skopiuj **adres e-mail** konta usługi (widoczny na liście / w „Szczegóły"), np. `raport-bot@twoj-projekt.iam.gserviceaccount.com`.

### 4. Udostępnij botowi folder na Drive
1. Na **https://drive.google.com** utwórz folder (np. „Raporty wywiadowcze").
2. Prawy klik na folder → **Udostępnij** (*Share*) → wklej adres e-mail konta usługi z kroku 3.4 → ustaw rolę **Edytor** (*Editor*) → **Wyślij/Gotowe**.
3. Wejdź do folderu i z paska adresu skopiuj jego **ID** — ciąg po `/folders/`, np.
   `https://drive.google.com/drive/folders/`**`1AbCdEfGhIjKlMnOpQr`** → ID = `1AbCdEfGhIjKlMnOpQr`.

### 5. Ustaw zmienne środowiskowe w Claude Code
Konfiguracja jest w interfejsie **claude.ai/code** (nie w Google, nie w GitHubie).

**Jak wejść do ustawień środowiska:**
1. Wejdź na **https://claude.ai/code**.
2. Kliknij **ikonę chmury z nazwą bieżącego środowiska** → otworzy się lista środowisk.
3. **Najedź** na swoje środowisko → po prawej kliknij **ikonę ustawień (zębatka)**.
4. W oknie znajdź pole **Environment variables** (zmienne środowiskowe).

**Co wpisać** — format `.env`, jedna para `KLUCZ=wartość` na linię, **bez cudzysłowów**:

| Zmienna | Wartość | Wymagana |
|---|---|---|
| `DRIVE_FOLDER_ID` | ID folderu z kroku 4.3 | ✅ tak |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | cała treść pliku JSON z kroku 3.3, **w jednej linii** | ✅ tak |
| `DRIVE_AS_GOOGLE_DOC` | `1` = Google Doc (domyślnie) / `0` = surowy .html | nie |

**Spłaszczenie klucza JSON do jednej linii** (plik z Google jest wielolinijkowy, a wartość musi być w jednej linii). Komenda kopiuje plik do schowka — klucz nie opuszcza Twojego komputera:

- **Windows (PowerShell):** `(Get-Content -Raw "C:\sciezka\klucz.json") -replace "\r?\n","" | Set-Clipboard`
- **Mac (Terminal):** `tr -d '\n' < ~/Downloads/klucz.json | pbcopy`

Następnie wklej zawartość schowka zaraz po `GOOGLE_SERVICE_ACCOUNT_JSON=` i zapisz.

> **Sekretów nie wklejaj do czatu** — wyłącznie do ustawień środowiska. Uwaga: Claude Code nie ma jeszcze dedykowanego sejfu na sekrety — zmienne widzi każdy, kto może edytować to środowisko (przy koncie prywatnym: tylko Ty). Klucz można w każdej chwili unieważnić w Google Cloud, a dostęp odebrać, usuwając konto usługi z udostępnienia folderu.

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
