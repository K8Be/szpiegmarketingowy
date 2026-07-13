# Automatyzacja — cotygodniowy raport mailem (Resend)

Cel: co **wtorek 9:00** raport generuje się sam i **automatycznie wychodzi mailem**. Twój udział po jednorazowym setupie: **zero**.

> **Dlaczego nie Google Drive?** Próbowaliśmy wariantu z kontem usługi (service account). Na **prywatnym Gmailu to niemożliwe**: konto usługi ma 0 GB własnego miejsca i nie może zapisać pliku (błąd `storageQuotaExceeded`), a przenieść własności pliku na Twoje 15 GB można tylko w Google Workspace. Dlatego dostarczamy mailem. (Skrypt `upload_to_drive.py` zostaje w repo, ale jest nieaktywny.)

## Jak to działa (2 klocki)
1. **Harmonogram (trigger, cron `0 9 * * 2`)** — odpala świeżą sesję Claude Code, która robi research (ostatnie 7 dni), aktualizuje bazę konkurentów i generuje nowy raport + wersję e-mail (HTML).
2. **Wysyłka** — ta sama sesja uruchamia `send_report.py`, który wysyła najnowszy raport przez **Resend API** (po HTTPS).

## Setup jednorazowy — po Twojej stronie

### Krok 1 — konto i klucz Resend (~5 min)
1. Załóż darmowe konto na **https://resend.com** (free tier: 3 000 maili/mies.).
2. **API Keys → Create API Key** → skopiuj klucz (zaczyna się od `re_...`).

### Krok 2 — ustaw zmienną w Claude Code
Wejdź w ustawienia środowiska (**claude.ai/code** → ikona chmury z nazwą środowiska → najedź → zębatka → **Environment variables**) i dodaj:

| Zmienna | Wartość | Wymagana |
|---|---|---|
| `RESEND_API_KEY` | klucz `re_...` z kroku 1 | ✅ tak |
| `REPORT_TO` | adres odbiorcy | nie (domyślnie `marketing@pracowniagier.com`) |
| `REPORT_FROM` | nadawca (patrz niżej) | nie |

> Zmienne po Drive (`DRIVE_FOLDER_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`) możesz **usunąć** — nie są już używane. Dla higieny warto też **unieważnić klucz konta usługi** w Google Cloud (Konta usługi → klucze → usuń).

### Krok 3 — wybór trybu wysyłki
Resend ma dwa tryby:

**A) Szybki test (bez własnej domeny) — działa od razu**
- Nadawca pozostaje domyślny `onboarding@resend.dev`.
- ⚠️ Ograniczenie Resend: bez zweryfikowanej domeny możesz wysyłać **tylko na adres e-mail, którym założyłaś konto Resend** (czyli najpewniej Twój Gmail). Ustaw wtedy `REPORT_TO` = ten sam adres.

**B) Docelowo na `marketing@pracowniagier.com` — wymaga weryfikacji domeny**
- W Resend: **Domains → Add Domain** → `pracowniagier.com` → dodaj wskazane rekordy **DNS** (SPF, DKIM) u operatora domeny. Po weryfikacji:
  - ustaw `REPORT_FROM` = `Szpieg Marketingowy <raport@pracowniagier.com>`,
  - `REPORT_TO` = `marketing@pracowniagier.com`.
- Wtedy maile wychodzą z domeny firmy i nie wpadają do spamu.

## Test ręczny (gdy ustawisz klucz)
```bash
python3 send_report.py --dry-run   # podgląd: co i do kogo (bez wysyłki)
python3 send_report.py             # realna wysyłka najnowszego raportu
```

## Awaryjnie
- Brak `RESEND_API_KEY` → skrypt kończy się jasnym komunikatem; raport i tak jest wygenerowany i zapisany w repo (nic nie ginie).
- Błąd API (np. wysyłka na obcy adres bez weryfikacji domeny) → kod `3` + treść odpowiedzi Resend w logu (najczęściej: użyj trybu A albo zweryfikuj domenę = tryb B).
