# Projekt: No More Blues (Magda) — koncert, 2 kamery + master WAV

Źródła: `/Volumes/Project 1/Video/Hermes Video Workspace/no-more-blues-magda-multicam/` (`BRIEF_AND_CHECKPOINT.md`, `GAMUT_MAPPING_USER_REFERENCE.md`, `analysis/sync.json`), kopia w `resolve-claude-recheck-20261109/04_production_history/`. **Nie uruchamiaj starych builderów** (`build_multicam.py` itd.) — nadpisałyby ręczne grade'y Dimy.

## Stan projektu w Resolve
- Projekt `No More Blues Magda Multicam 20261102-213037`; zatwierdzony roboczy timeline `FULL PERFORMANCE — quality-first multicam v1` (ID `eeb68b95-…`) — **stacked edit** (A na V1, 4 wstawki B na V2, WAV na A1), nie native multicam.
- 09.11 dodano osobny `NATIVE MULTICAM LAB — No More Blues 20261109 — UNGRADED` (native A+B, bez grade'u) — laboratorium, nie montaż.
- **09.11 wieczorem (Claude): prawdziwy montaż multicam** `No More Blues — MULTICAM CUT v1 — 20261109` w binie `MULTICAM — No More Blues (рабочий)`: 19 elementów jednego klipu multicam `d59c5c5b` (w nazwie „UNGRADED", ale grade jest na elementach timeline'u), grade Dimy skopiowany z `FULL PERFORMANCE` (A ← V1, B ← wstawka 296–422 z Gamut Mapping). Bez `SaveProject`. Plan cięć, DRT, dowody: `/Volumes/Project 1/Video/Hermes Video Workspace/multicam-cut-claude-20261109/`. Testowe timeline'y/klipy Hermesa i Claude przeniesione (nie usunięte) do binu `_ЛАБОРАТОРИЯ 20261109 — учебное`.
- Grade v1 (09.11, 22:15): wzorce Dimy — kawałek 16 (B, sala: Temp −200, Gain G 1.15, Sat 45, Hue vs Sat w dół na niebieskim/fiolecie) na wszystkie B, kawałek 17 (A: Hue vs Sat w górę na żółto-pomarańczowym ×1.72 i lekko turkus) na wszystkie A. Pomiary przed/po: `multicam-cut-claude-20261109/VECTOR_TRANSFER.txt`.
- Treść B (czas mastera): 0–10 s duet, widać gitarzystę z gitarą; 10–14 najazd; 14–26 zbliżenia wokalistki (z ręki); 26–31 przekadrowanie; 31–92 stabilny duet z gitarą; 92–96 kamera odchodzi; 97–106 sala i publiczność; 106–109 ruch; 110–139,6 sala z tyłu, scena z daleka. Na A gitary nie widać. Po 139,6 s jest tylko A (~153 s) — bez cyfrowego zoomu.
- Ręczne poprawki Dimy (środkowe klipy) są nowsze niż `resolve/No-More-Blues-Magda-picture-v1.mov` — ten render **nie** jest aktualnym finałem.

Dowody laboratorium multicam (09.11) w `resolve-claude-recheck-20261109/`: `09_multicam_lab/NATIVE_MULTICAM_RECEIPT.json`, `09_multicam_lab/B_ALIGNMENT_RECEIPT.json`, `09_multicam_lab/FRAME_FORMAT_QA.json`, kontrola 10 bit: `HERMES_v1.2_REVIEW_CHECKS.json`.

## Kamery i synchronizacja
- **A** = główna kamera (lepsza jakość). Ma PTS startu ~0,1057 s — nie zeruj obrazu względem dźwięku bez kompensacji; znormalizowany `A-CFR30-ProResLT.mov` już to uwzględnia.
- **B** = WhatsApp/Topaz prob-4; większa rozdzielczość ≠ więcej detali.
- **Znak opóźnienia:** czas pliku B ≈ czas mastera **+48,6415 s**; w CFR30 stosowano **1459 klatek = 48,6333 s**. Nie odwracaj znaku. Pomiar z korelacji audio w sali — bez obietnicy dokładności subklatkowej.
- **B synchronicznie pokrywa tylko master 0–~139,6 s.** Po tej granicy nie wstawiaj B jako synchronicznego wykonania.
- Ważne momenty A: ok. 200 / 230 / 260 s.

## Audio
- Master: `/Volumes/Project 1/1/Audio/No More Blues Magda.wav`, PCM24/48k stereo, ~−7,7 LUFS / −0,7 dBTP — gotowy master muzyczny. Ciągły przez wszystkie cięcia; dźwięk kamer tylko do synchronizacji. Bez presetów mowy.

## Kolor — prośba Dimy: „zapamiętaj ten gamut limiter"
OFX **Gamut Mapping** na węźle (wartości ze zrzutów Dimy; odczyt/zapis tych parametrów przez naszą ścieżkę API nie został potwierdzony):
Gamma: Use timeline · Tone Mapping: DaVinci · Max In/Out Luminance 100/100 · Avg Input Luminance 9 · **Gamut Mapping Method: Saturation Compression · Saturation Knee 0.900 · Saturation Max 1.000** · Forward/Inverse OOTF: Off.
Przydatne przy nasyconym niebiesko-purpurowym świetle sceny; nie uniwersalny preset i nie zamiennik globalnego obniżenia saturacji. Zachowaj atmosferę światła; sprawdzaj twarze w kolorowym LED przed/po.

## Montaż — prośba Dimy
4 wstawki / ~94 % A było za mało. Częstsze, sensowne przejścia w strefie pokrycia obu kamer; orientacyjnie ujęcia ~6–12 s zgodnie z frazami, gestami, jakością kadru (propozycja, nie uzgodniony rytm). Kolejną wersję rób na **kopii** aktualnego timeline Dimy; plan cięć do akceptacji (zasada 8 w SKILL.md).
