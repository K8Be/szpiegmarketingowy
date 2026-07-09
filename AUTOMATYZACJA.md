# Automatyzacja — cotygodniowa wysyłka raportu (Resend API)

Cel: co **wtorek 9:00** raport generuje się sam i **automatycznie wychodzi mailem** na `marketing@pracowniagier.com`.
Twój udział po jednorazowym setupie: **zero**.

## Jak to działa (2 klocki)
1. **Harmonogram (trigger, cron `0 9 * * 2`)** — odpala świeżą sesję Claude Code, która robi research (ostatnie 7 dni), aktualizuje bazę konkurentów i generuje nowy raport + wersję e-mail (HTML).
2. **Wysyłka** — ta sama sesja uruchamia `send_report.py`, który wysyła najnowszy raport przez **Resend API** (po HTTPS).

## Setup jednorazowy (ok. 10 minut) — po Twojej stronie
1. Załóż darmowe konto na **https://resend.com** (free tier: 3 000 maili/mies., w zupełności wystarczy).
2. Wygeneruj **API Key** (Dashboard → API Keys → Create).
3. **(Zalecane do produkcji)** Zweryfikuj domenę `pracowniagier.com` w Resend (Dashboard → Domains → dodajesz rekordy DNS: SPF, DKIM). Dzięki temu nadawca będzie wyglądał firmowo, np. `raport@pracowniagier.com`, i maile nie wpadną do spamu.
   - **Na szybki test** możesz to pominąć — skrypt użyje domyślnego nadawcy `onboarding@resend.dev` (Resend pozwala wysłać na dowolny adres w trybie testowym).
4. Ustaw w **konfiguracji środowiska Claude Code** (Environment → Environment Variables / Secrets) następujące zmienne:

   | Zmienna | Wartość | Wymagana |
   |---|---|---|
   | `RESEND_API_KEY` | klucz z kroku 2 | ✅ tak |
   | `REPORT_TO` | `marketing@pracowniagier.com` | nie (to jest domyślna) |
   | `REPORT_FROM` | `Szpieg Marketingowy <raport@pracowniagier.com>` | nie (dopiero po weryfikacji domeny) |

   > **Sekretów nie wklejaj do czatu** — wyłącznie do konfiguracji środowiska. To bezpieczniejsze i można je w każdej chwili odwołać w Resend.

## Test ręczny (gdy ustawisz klucz)
```bash
python3 send_report.py --dry-run   # podgląd: co i do kogo poszłoby (bez wysyłki)
python3 send_report.py             # realna wysyłka najnowszego raportu
```

## Zmiana odbiorcy / dodanie kopii
- Inny adres: zmień `REPORT_TO`.
- Kopia do Ciebie: najprościej dodać regułę przekierowania w Resend albo rozszerzyć `to` w `send_report.py` o listę adresów.

## Awaryjnie / gdy coś nie zadziała
- Brak `RESEND_API_KEY` → skrypt kończy się kodem `2` i wypisuje jasny komunikat; raport i tak zostaje wygenerowany i zapisany w repo (nic nie ginie).
- Błąd API (np. niezweryfikowana domena) → kod `3` + treść odpowiedzi Resend w logu.
