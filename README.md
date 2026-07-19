# Szpieg Marketingowy — cotygodniowy raport wywiadowczy

Automatyczny raport konkurencyjno-trendowy dla **Pracowni Gier Szkoleniowych** (pracowniagier.com).

## Cel
Co tydzień dostarczyć managerowi marketingu skanowalny (20 min) raport:
1. **Część 1** — nowe działania konkurencji (ostatnie 7 dni)
2. **Część 2** — 3–5 świeżych trendów w corporate learning / teambuilding / L&D + pomysły na wdrożenie
3. **Część 3** — 3–5 rekomendacji operacyjnych (co / po co / nakład S/M/L / właściciel)

## Harmonogram
Uruchomienie: **każdy poniedziałek 4:00 czasu polskiego** (cron `0 2 * * 1` w UTC = 4:00 CEST latem).

## Struktura repo
- `raporty/RRRR-MM-DD-raport-wywiadowczy.md` — kolejne wydania (jeden plik na tydzień).
- `baza/konkurenci.md` — żywa baza konkurentów aktualizowana przyrostowo.

## Zasada przyrostowości
Raport #1 (`2026-07-09`) jest **bazowy** — buduje mapę konkurencji. Od raportu #2 każdy wpis w Części 1
ma mieć **datę i link** do konkretnego działania (post / LP / kampania / event). Bez świeżego sygnału:
piszemy „brak istotnych sygnałów w tym tygodniu".

## Źródła trendów (preferowane)
Training Industry, Chief Learning Officer, LinkedIn Learning / Workplace Learning Report, HBR,
McKinsey, Deloitte HR Trends, ATD, Gartner, oraz posty branżowych liderów opinii na LinkedIn.
