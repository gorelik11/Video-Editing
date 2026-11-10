---
name: davinci-resolve
description: Use for ANY work with DaVinci Resolve or Final Cut Pro on the M4 — colour grading interview/archive footage, building timelines, rendering clips, Resolve scripting (DaVinciResolveScript), the davinci-resolve or fcpxml MCP servers, FCPXML round-trips, and assembling teasers/Shorts where Resolve grades and ffmpeg assembles. Also when a Resolve MCP call fails ("Resolve not running", scriptapp returns None), when footage looks overexposed/flat after grading, or when interview levels differ between speakers. Russian triggers — "давинчи", "резолв", "грейдинг", "цветокоррекция", "отрендери клипы", "файнал кат", "fcpxml", "тизер", "собери ролик".
version: 1.0.0
metadata:
  hermes:
    tags: [video, davinci-resolve, final-cut-pro, fcpxml, ffmpeg, grading, mcp]
    related_skills: [ai-shorts-pipeline, free-video-production]
---

# DaVinci Resolve + Final Cut Pro (M4)

Zbudowane na realnym projekcie „Teaser Dom 2026-10" (zwiastun filmu TVP o Dimie Goreliku):
`/Volumes/KINGSTON/Video Production/projects/teaser-dom-2026-10/` — `resolve_grade.py` (grading w Resolve),
`teaser_v4.py` (montaż w ffmpeg), `smartcrop.py` (kadr 9:16). Kopiuj stamtąd wzorce zamiast pisać od zera.

## Zasady nienegocjowalne

1. **Nie aktualizuj Resolve.** M4 ma DaVinci Resolve Studio 21.0.0b28 (beta) — skrypty działają; aktualizacja może je zepsuć.
2. **Resolve musi być otwarty** i mieć Preferences → General → External scripting using = **Local**. Bez tego `dvr.scriptapp("Resolve")` zwraca `None`, a MCP zgłasza „not running". Nie diagnozuj dalej — poproś o otwarcie Resolve.
3. **Transkrypcja tylko lokalnie** (`whisper-cli`, model `~/Models/whisper/ggml-large-v3-turbo.bin`). Nie ustawiaj `ELEVENLABS_API_KEY` — wysłałoby audio na zewnątrz.
4. **Żadnego gołego `pip`.** Każde narzędzie we własnym venv (`~/.venvs/<nazwa>`, Homebrew Python 3.12).
5. Ciężkie pliki (ProRes, render, work/) → `/Volumes/Project 1/Video/<projekt>/`; skrypty i notatki → `Video Production/projects/<projekt>/` (repo git).
6. Publikacja (YouTube, wysyłka) zawsze po akceptacji Dimy. Widoczność filmów na YouTube zmienia tylko Dima.

## Podział pracy: co w Resolve, co w ffmpeg

| Zadanie | Narzędzie | Dlaczego |
|---|---|---|
| Korekcja barwna wywiadów (CDL), render pojedynczych klipów | **Resolve** (skrypt lub MCP) | prawdziwy pipeline koloru, ProRes 422 HQ |
| Montaż, napisy ASS, plansze, kadr 9:16, miks audio, eksport H.264 | **ffmpeg-full** (`/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`) | deterministyczny, powtarzalny jednym poleceniem, łatwy diff wersji |
| Montaż ręczny / multicam / poprawki Dimy | **Final Cut Pro** (FCPXML + MCP `fcpxml`) | Dima pracuje w FCP; FCPXML pozwala edytować cięcia jako tekst |

Wzorzec: Resolve renderuje **tylko zgradowane fragmenty z zapasem 0,5 s** (`graded/*.mov`), a cały montaż składa skrypt ffmpeg. Zmiana tekstu planszy czy cięcia = edycja jednej linii i ponowne uruchomienie, bez otwierania Resolve.

## Dwa sposoby sterowania Resolve

- **MCP `davinci-resolve`** (37 narzędzi: project, media pool, timeline, timeline_item_color, graph, render, fusion_comp, lut, dctl, knowledge…) — do pracy interaktywnej i sprawdzania stanu („co jest na timeline", „pokaż węzły").
- **Skrypt Pythona** (`~/.venvs/davinci-resolve-mcp/bin/python skrypt.py`) — do operacji wsadowych, które trzeba powtórzyć. Szkielet: `resolve_grade.py`. Kroki:
  1. `pm.LoadProject(name) or pm.CreateProject(name)`; ustaw `timelineResolutionWidth/Height`, `timelineFrameRate`, `timelineInputResMismatchBehavior=scaleToCrop`.
  2. `mp.ImportMedia([path])` raz na plik źródłowy.
  3. `mp.CreateEmptyTimeline(nazwa_z_godziną)` — nowa nazwa za każdym razem (duplikat nazwy = `None`).
  4. `mp.AppendToTimeline([{"mediaPoolItem", "startFrame", "endFrame"}])` — klatki **źródła**, `endFrame` włącznie (dlatego `-1`).
  5. `ti.SetCDL({"NodeIndex": "1", "Slope": "r g b", "Offset": ..., "Power": ..., "Saturation": "x"})` — wszystkie wartości jako **stringi**.
  6. `proj.SetCurrentRenderMode(0)` (osobne klipy), `SetCurrentRenderFormatAndCodec("mov", "ProRes422HQ")`, `SetRenderSettings({... "UniqueFilenameStyle": 1})`, `AddRenderJob()`, `StartRendering([job])`, pętla `IsRenderingInProgress()`.
  7. Resolve nadaje plikom nazwy generyczne — **przemianuj je po kolejności klipów na timeline** i odłóż stare wersje do `graded_v1/` itd.

## Grading — czego się nauczyliśmy

- Materiał wywiadowy (płaski, niski kontrast): zaczynaj od `Slope ~1.05, Offset -0.03…-0.04, Power ~1.05–1.10, Saturation 1.08–1.18`.
- **Skóra przede wszystkim.** „Chłodny" slope z dużym niebieskim (np. `1.04 1.08 1.16`) przy zbyt niskim Power przepalił twarz rozmówcy. Po każdej zmianie wyciągnij klatkę z twarzą i obejrzyj ją.
- **Porównuj warianty przed renderem** symulacją CDL w ffmpeg (`lutrgb` z wyrażeniem slope/offset/power) na 2–3 klatkach obok siebie — szybciej niż renderować w Resolve.
- Archiwum SD (720×576, SAR ≠ 1): najpierw `scale=iw*sar:ih,setsar=1`. **Nie powiększaj na cały kadr HD** — rozmyte. Daj okno ~1,6× SD (`scale=W*0.62`) na rozmytym, przyciemnionym tle z tego samego obrazu (`gblur=50, eq=brightness=-0.28`), lekki `unsharp` i ziarno.
- Wypalone napisy w archiwum (np. RTVi): przytnij dolne ~26% (`crop=iw*0.94:ih*0.71:iw*0.03:ih*0.03`).

## Audio w montażu

- Każdą wypowiedź normalizuj osobno: `loudnorm=I=-16:TP=-1.5:LRA=11` (cel −16 LUFS, cały zwiastun wychodzi ~−14 LUFS — tyle, ile normalizuje YouTube).
- **Jeśli rozmówca „brzmi ciszej" mimo tych samych LUFS — sprawdź szum tła:** `astats` → `Noise floor dB`. Szum pomieszczenia (u jednego rozmówcy −28 dB wobec −75 dB u drugiego) jest wliczany do głośności, więc sam głos ląduje niżej. Leczenie: `highpass=f=90,afftdn=nr=14:nf=-35,equalizer=f=3000:t=q:w=1:g=3` przed loudnorm i `volume=+2…3dB` po nim — ostateczna ocena na słuch Dimy.
- Weryfikacja: `ebur128` dla każdego okna osobno na **miksie** i na **ścieżce samej mowy** — różnica pokazuje, ile dokłada podkład muzyczny.
- Cięcia w mowie: transkrypcja whisper ma zgrubne czasy słów; dokładny punkt cięcia znajdź krótką transkrypcją okna + RMS (szukaj ciszy przed „eee").

## Napisy, plansze, miniatury

- Napisy i plansze końcowe: plik ASS (`subtitles=filename=...`), styl `SF Pro Display`; imię zawsze **„Dima Gorelik" bez odmiany**.
- `drawtext` z `font='Helvetica Neue:style=Bold'` cicho spada do nie-pogrubionego fontu — używaj `fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf'`.
- Miniatura YouTube 1280×720: porównanie „wtedy / dziś" (klatka z archiwum + portret) mocno działa. Polecenie do odtworzenia trzymaj obok w repo.
- Pionowa plansza 1080×1920: długie linie `CardSmall` się zawijają — skróć tekst albo zwiększ odstęp.

## Kadr 9:16 — „skaczące klatki”

- Skok kadru w punktach kontrolnych stawiaj **dokładnie na cięciu źródła** (`scdet=threshold=8` na fragmencie), nie „na oko” — różnica 0,08 s = 1–2 klatki złego kadru, widoczne jako podskok.
- Auto-kadr (`smartcrop.py`): w ujęciu jedna prosta (polyfit) z limitem prędkości, nie średnia ruchoma — ta „pływała” tam i z powrotem.
- Kontrola: różnice klatek + `phaseCorrelate` (dwa duże skoki pod rząd = kadr przestawiony obok cięcia) i arkusz klatek wokół każdego cięcia.

## Weryfikacja przed oddaniem

1. Klatka z planszy końcowej i z każdej twarzy (`-ss T -frames:v 1`), obejrzana.
2. `ebur128` całości i odcinków; `TP ≤ −1 dBTP`.
3. `ffprobe` — długość, fps 25, `yuv420p`, AAC 256k, `+faststart`.
4. Wersjonuj pliki wyjściowe (`_v8`, `_v9`), nie nadpisuj zatwierdzonej wersji.

## Final Cut Pro

- M4 ma FCP 12.2; starsze projekty żyją na laptopie Big Sur (FCPXML 1.8).
- Przepływ: FCP → `File → Export XML…` do `Video Production/projects/` → edycja przez MCP `fcpxml` (15 narzędzi, `fcp-mcp-server==0.27.2` przez `uvx`) → import z powrotem.
- MCP widzi tylko katalogi z `FCP_PROJECTS_DIRS`: `Video Production/projects` i `/Volumes/Project 1/Video`.
- Dokumentacja formatu: `Video Production/docs/fcpxml-reference.md`, multicam/fps: `docs/fcpxml-multicam-framerate-conversion.md`.

## Instalacja MCP (Claude Code i Hermes)

Patrz `references/install-mcp.md` — gotowe polecenia dla obu klientów i smoke test.
