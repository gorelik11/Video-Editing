---
name: davinci-resolve
description: Use for ANY work with DaVinci Resolve or Final Cut Pro on the M4 — colour grading interview/archive/concert footage, building timelines, rendering clips, Resolve scripting (DaVinciResolveScript), the davinci-resolve or fcpxml MCP servers, Color nodes/CDL/LUT/DRX curves, Fusion comps, native multicam (CreateMulticamClip), IntelliSearch, scopes (waveform, parade, vectorscope), FCPXML round-trips, and assembling teasers/Shorts where Resolve grades and ffmpeg assembles. Also when a Resolve MCP call fails ("Resolve not running", scriptapp returns None), when an appended clip is a frame short/long, when footage looks overexposed/flat after grading, or when interview levels differ between speakers. Russian triggers — "давинчи", "резолв", "грейдинг", "цветокоррекция", "ноды", "кривые", "скопы", "мультикам", "вектороскоп", "отрендери клипы", "файнал кат", "fcpxml", "тизер", "собери ролик".
version: 1.2.0
metadata:
  hermes:
    tags: [video, davinci-resolve, final-cut-pro, fcpxml, ffmpeg, grading, fusion, scopes, mcp]
    related_skills: [ai-shorts-pipeline, free-video-production]
---

# DaVinci Resolve + Final Cut Pro (M4)

Zbudowane na realnym projekcie „Teaser Dom 2026-10" (zwiastun filmu TVP o Dimie Goreliku):
`/Volumes/KINGSTON/Video Production/projects/teaser-dom-2026-10/` — `resolve_grade.py` (grading w Resolve),
`teaser_v4.py` (montaż w ffmpeg), `smartcrop.py` (kadr 9:16). Kopiuj stamtąd wzorce zamiast pisać od zera.

v1.1 (2026-11-09) dodaje to, co Hermes sprawdził na Resolve **21.1.1.10** + MCP v4.15.2 na syntetycznym materiale
([dowody i ograniczenia](references/resolve-21.1-qualification.md), [źródła badań](references/research-map.md)).
Recepty z v1.0 pochodzą z 21.0.0b28 i **nie zostały automatycznie przetestowane ponownie na 21.1.1** — przy pierwszym użyciu sprawdź na krótkim klipie.
Poprzednia wersja: [references/SKILL_v1.0.md](references/SKILL_v1.0.md). v1.2 — po audycie Hermesa i niezależnej kontroli Claude (multicam, Fusion, bramka zapisu, skopy 10 bit).

**Trzy poziomy dowodu — nie mieszaj:** *przetestowane lokalnie* (odczyt zwrotny / piksele) · *jest w zainstalowanym API/MCP, nietestowane* · *nie znalezione na naszej ścieżce*. Sukces wywołania ≠ efekt; efekt techniczny ≠ akceptacja Dimy.

## Zasady nienegocjowalne

1. **Nie aktualizuj Resolve.** Aktualizuje wyłącznie Dima. Teraz: DaVinci Resolve Studio **21.1.1** (sprawdź na żywo `GetVersionString()`). Aktualizacja może zepsuć skrypty — po zmianie wersji Dimy przekalibruj granice klatek (niżej).
2. **Resolve musi być otwarty** i mieć Preferences → General → External scripting using = **Local**. Bez tego `dvr.scriptapp("Resolve")` zwraca `None`, a MCP zgłasza „not running" — ale `None` może mieć też inne przyczyny. Wolno diagnozować tylko do odczytu (czy proces działa, który Python/moduł, zmienne środowiskowe); preferencji nie zmieniaj — poproś Dimę. Brak połączenia nie upoważnia do instalacji ani aktualizacji.
3. **Transkrypcja tylko lokalnie** (`whisper-cli`, model `~/Models/whisper/ggml-large-v3-turbo.bin`). Nie ustawiaj `ELEVENLABS_API_KEY` — wysłałoby audio na zewnątrz. Klatek i materiału nie wysyłaj do chmurowych modeli bez osobnej zgody.
4. **Żadnego gołego `pip`.** Każde narzędzie we własnym venv (`~/.venvs/<nazwa>`, Homebrew Python 3.12).
5. Ciężkie pliki (ProRes, render, work/) → `/Volumes/Project 1/Video/<projekt>/`; skrypty i notatki → `Video Production/projects/<projekt>/` (repo git).
6. Publikacja (YouTube, wysyłka) zawsze po akceptacji Dimy. Widoczność filmów na YouTube zmienia tylko Dima.
7. **Trzy osobne zgody w projekcie Dimy** (nie łącz ich w jedną):
   - `SaveProject` (i eksport/backup, który utrwala niezapisany stan) — tylko po wyraźnej zgodzie na zapisanie *bieżącego* stanu. Jednorazowa zgoda nie jest stałym pozwoleniem.
   - **Przełączenie projektu** — dopiero po uzgodnieniu z Dimą, co zrobić z niezapisanymi zmianami.
   - **`ApplyGradeFromDRX`** — tylko na zatwierdzonej kopii (duplikat timeline/projektu): DRX **zastępuje** cały graf węzłów, nie dopisuje do niego.
   Dotyczy też `LoadProject`/`CreateProject` w przepisie niżej i automatycznego „przywracania" stanu.
8. **Bramka zapisu na timeline Dimy.** Każda wstawka/zmiana: plan (tabela kandydatów: źródło, in/out, zegar odniesienia, długość, powód, must/nice) → akceptacja → ponowny odczyt stanu tuż przed zapisem (zajęte przedziały + odcisk planu) → jeden zapis → odczyt zwrotny. Przygotowanie w tle (napisy, assety poza projektem) jest OK w już uzgodnionym zakresie; **utworzenie** nowego timeline/wariantu A/B w projekcie Dimy to też zapis — za zgodą. Wstawienie — dopiero po zgodzie. Bez masowych zapisów „na wszystkie klipy".
   Nowsze ręczne grade'y Dimy mają pierwszeństwo przed starymi skryptami montażowymi — nigdy nie uruchamiaj starych builderów, żeby „odtworzyć" stan.

## Podział pracy: co w Resolve, co w ffmpeg

| Zadanie | Narzędzie | Dlaczego |
|---|---|---|
| Korekcja barwna wywiadów (CDL), render pojedynczych klipów | **Resolve** (skrypt lub MCP) | prawdziwy pipeline koloru, ProRes 422 HQ |
| Montaż, napisy ASS, plansze, kadr 9:16, miks audio, eksport H.264 | **ffmpeg-full** (`/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`) | deterministyczny, powtarzalny jednym poleceniem, łatwy diff wersji |
| Montaż ręczny / multicam / poprawki Dimy | **Final Cut Pro** (FCPXML + MCP `fcpxml`) | Dima pracuje w FCP; FCPXML pozwala edytować cięcia jako tekst |

Wzorzec: Resolve renderuje **tylko zgradowane fragmenty z zapasem 0,5 s** (`graded/*.mov`), a cały montaż składa skrypt ffmpeg. Zmiana tekstu planszy czy cięcia = edycja jednej linii i ponowne uruchomienie, bez otwierania Resolve.
Wyjątek: jeśli Dima prosi o **edytowalny** montaż w Resolve, ffmpeg tylko przygotowuje materiały (assety, remux, QC), a timeline/grade/Fusion zostają w Resolve.

## Dwa sposoby sterowania Resolve

Kanały (wybierz świadomie): **wbudowany MCP Resolve 21.1** — nietestowany · **MCP samuelgursky v4.15.2** (niżej) · **skrypt Fusion** (bezpośrednie operacje na grafie Fusion — nie wszystkie ukryte/pluginowe parametry; nie Color) · **UI / Computer Use** (wymaga `cua-driver`) · **analiza pikseli** z wyeksportowanej klatki.

- **MCP `davinci-resolve`** (`/Users/macbook/projects/davinci-resolve-mcp/src/server.py`; 37 narzędzi złożonych: project, media pool, timeline, timeline_item_color, graph, render, fusion_comp, lut, dctl, knowledge…) — do pracy interaktywnej i sprawdzania stanu. To nie jest „pełna kontrola Resolve". Szczegółowe procedury („kernels") per obszar: `~/projects/davinci-resolve-mcp/docs/kernels/` (fusion-composition, color-grade, timeline-edit, render-deliver, timeline-conform-interchange, media-pool-ingest, audio-fairlight…) — to dokumentacja autora MCP, nie nasza kwalifikacja.
- **Skrypt Pythona** (`~/.venvs/davinci-resolve-mcp/bin/python skrypt.py`, moduł `DaVinciResolveScript` z `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules`; nie potrzeba żadnego klucza chmurowego) — do operacji wsadowych. Aktualna dokumentacja API: `Developer/Scripting/DaVinciResolveScript.pyi`, `README.md`, `CHANGELOG.md` (stary `README.txt` kończy się na 21 beta). Szkielet: `resolve_grade.py`. Kroki:
  1. `pm.LoadProject(name) or pm.CreateProject(name)`; ustaw `timelineResolutionWidth/Height`, `timelineFrameRate`, `timelineInputResMismatchBehavior=scaleToCrop`.
  2. `mp.ImportMedia([path])` raz na plik źródłowy. **Wynik może mieć inną kolejność niż wejście** — mapuj po `GetClipProperty('File Path')`, sprawdź ścieżkę i długość, nigdy nie zipuj list.
  3. `mp.CreateEmptyTimeline(nazwa_z_godziną)` — nowa nazwa za każdym razem (duplikat nazwy = `None`).
  4. `mp.AppendToTimeline([{"mediaPoolItem", "startFrame", "endFrame"}])` — klatki **źródła**. `endFrame` jest **wyłączny** (`0..30` → 30 klatek), więc **bez `-1`**. Zaobserwowane na 21 beta (No More Blues, `endFrame=startFrame+duration`) i na 21.1.1 (test syntetyczny). Stary `resolve_grade.py` (teaser) używał `-1` — to sprzeczne z obecnym testem 21.1.1 i wcześniejszym raportem No More Blues na 21 beta. Historycznych plików teasera nie zmierzono ponownie; nie traktuj tego jako dowodu zmiany semantyki między wersjami. Po każdej zmianie wersji sprawdź na klipie testowym i porównaj `GetDuration()`. Dotyczy tylko `AppendToTimeline`: render `MarkIn/MarkOut` jest **włączny** (`0..29` → 30 klatek).
  5. `ti.SetCDL({"NodeIndex": "1", "Slope": "r g b", "Offset": ..., "Power": ..., "Saturation": "x"})` — wszystkie wartości jako **stringi**.
  6. `proj.SetCurrentRenderMode(0)` (osobne klipy), `SetCurrentRenderFormatAndCodec("mov", "ProRes422HQ")`, `SetRenderSettings({... "UniqueFilenameStyle": 1})`, `job = AddRenderJob()` (zachowaj **zwrócone** ID), `StartRendering([job])`, pętla z `time.sleep` po `GetRenderJobStatus(job)` (status, `CompletionPercentage`, błąd) — nigdy pusta pętla `while …: pass` ani `GetRenderJobStatus(0)`. Formaty/kodeki odkrywaj przez `GetRenderFormats()`/`GetRenderCodecs()`. Timeout nie oznacza anulowania — sprawdź status zadania przed ponowieniem; nie przełączaj strony/projektu w trakcie renderu.
  7. Resolve nadaje plikom nazwy generyczne — renderuj do **pustego** katalogu, przemianuj po kolejności klipów na timeline, ale sprawdź dopasowanie (liczba plików, długości, klatka kontrolna), a stare wersje odłóż do `graded_v1/` itd.
  8. Na koniec przywróć i odczytaj projekt/timeline/stronę/playhead, które Dima miał otwarte.

## Pułapki API (sprawdzone na 21.1.1)

- **Indeksy MCP są mieszane:** `item_index` od **0**, ścieżki i węzły od **1**. Narzędzie `graph` domyślnie bierze graf **timeline**, nie klipu — podawaj `source="item"` oraz jawnie track/item.
- MCP może zwrócić `_operation.status=success` przy `verification.status=unverified` — sukces wywołania ≠ zweryfikowany efekt.
- Uruchamiając MCP jako proces potomny, czytaj stderr osobno (może zablokować potok). Wyłącz sprawdzanie aktualizacji: `DAVINCI_RESOLVE_MCP_UPDATE_CHECK=0`, `DAVINCI_RESOLVE_MCP_UPDATE_MODE=never`.
- **Fusion `SetInput` zwraca `None`, nawet gdy zapis się udał.** Nie testuj wartości zwracanej — sprawdzaj przez `GetInput`.
- **Seek ≠ nowy obraz.** Po `SetCurrentTimecode` eksport może dać poprzednią klatkę mimo `True`. W No More Blues pomogło odczekanie ~0,6 s (obserwacja, nie gwarancja) + timecode przed i po + weryfikacja tożsamości obrazu (porównanie z klatką źródła). `GetCurrentVideoItem()` potrafi zwrócić poprzednio zaznaczony klip — oczekiwane źródło wyznaczaj z najwyższego włączonego elementu; przy compound/multicam/Fusion/przezroczystości to nie wystarcza — porównuj piksele.
- Skrypty kwalifikacyjne Hermesa (`resolve-skill-qualification-20261109/`) to jednorazowa diagnostyka, która kontynuuje po błędach — nie uruchamiaj ich ponownie w produkcji. Kod produkcyjny ma się zatrzymać przed zależnym, niebezpiecznym zapisem.
- Przed wstawieniem na timeline odczytaj zajęte przedziały `[start,end)` tuż przed zapisem (zasada 8). To nie jest blokada — tylko jeden piszący naraz.
- **Timeout ≠ anulowanie** (render, transkrypcja natywna): najpierw sprawdź, czy zadanie trwa lub już dało wynik, dopiero potem decyduj o ponowieniu. Natywna transkrypcja Resolve i lokalny whisper to różne kanały.
- **IntelliSearch:** API ma `AnalyzeForIntellisearch` (MediaPoolItem/Folder) i `ResetIntellisearchAnalysis` (Project) — to tylko *uruchomienie analizy*, nie API wyszukiwania z wynikami in/out. Nietestowane; bez zgody Dimy nie indeksuj archiwum. Clipto i inne zewnętrzne wyszukiwarki — niezainstalowane, prywatność niesprawdzona.
- Edycje typu move/trim/transition vs usuń-i-wstaw-ponownie: relacje z Reddita są sprzeczne co do zachowania grade'ów, Fusion, retime i audio. Przed taką operacją na materiale Dimy — test zachowania na kopii.

## Węzły Color ≠ Fusion

- **Przetestowane lokalnie** (istniejący węzeł): `SetCDL` (piksele się zmieniają), `CopyGrades`, `ExportLUT` (33 pkt), bypass węzła (przywraca piksele dokładnie), `GetNumNodes`/`GetNodeLabel`/`GetToolsInNode`, krzywa Y przez DRX (niżej).
- **W zainstalowanym API, nie testowane ponownie:** `SetLUT`/`GetLUT`, wersje grade'u, grupy kolorów (pre/post graph), `GrabStill`/`ExportStills`, Magic Mask, Stabilize.
- **Nie znalezione na naszej ścieżce** (scripting + MCP v4.15.2): tworzenie i łączenie węzłów, koła primaries poza CDL, edycja punktów krzywych, HSL, kwalifikatory, okna, odczyt/zapis parametrów OFX (np. `Gamut Mapping` — widać tylko nazwę narzędzia; DRX z parametrami OFX nietestowany).

- **Krzywa Y przez DRX** (przetestowane): lokalny generator `/Users/macbook/projects/davinci-resolve-mcp/resolve-advanced/vendor/drx-codec/drx-generator.js` → `item.GetNodeGraph().ApplyGradeFromDRX(path, 0)` (0 = bez keyframe'ów). Liczba węzłów, etykiety i Custom Curves się odczytują, piksele renderu się zmieniają. DRX **zastępuje graf** → tylko na kopii (zasada 7). Wartość rzędnej krzywej ≠ dokładny kod wyjściowy; jednostki UI, CDL i generatora się różnią. Identyczny DRX nie jest kopią zapasową grade'u Dimy.
- Fusion `ColorCorrector` + `EllipseMask` to nie Power Window z Color. Szeroki dostęp do Fusion nie oznacza takiej samej kontroli nad Color.
- **Procedura Fusion** (wg `docs/kernels/fusion-composition-kernel.md`): rozróżnij comp elementu timeline (`GetFusionCompByIndex`) od aktywnej strony Fusion → inspekcja comp, narzędzi i portów → dry-run dodania → dodanie narzędzia → zapis wejść **z odczytem `GetInput`** → połączenie (np. z `MediaOut1` — narzędzie bez połączenia nic nie pokazuje) → eksport `.comp`/`.setting` → render/klatka kontrolna. Nazwa `safe_*` w MCP nie czyni operacji bezpieczną. Offline generowanie `.comp` to co innego niż zastosowanie na żywo. Bez bezpośrednich edycji `Project.db`.
- Ustawienia Gamut Mapping Dimy (Saturation Compression) to punkt odniesienia dla tamtego materiału, nie uniwersalny preset.

## Grading — czego się nauczyliśmy

- Materiał wywiadowy (płaski, niski kontrast): zaczynaj od `Slope ~1.05, Offset -0.03…-0.04, Power ~1.05–1.10, Saturation 1.08–1.18`.
- **Skóra przede wszystkim.** „Chłodny" slope z dużym niebieskim (np. `1.04 1.08 1.16`) przy zbyt niskim Power przepalił twarz rozmówcy. Po każdej zmianie wyciągnij klatkę z twarzą i obejrzyj ją.
- **Koncerty:** zachowaj kolorowe światło sceny (niebieskie/magenta) — nie ciągnij każdej twarzy na linię skóry.
- **Porównuj warianty przed renderem** symulacją CDL w ffmpeg (`lutrgb` z wyrażeniem slope/offset/power) na 2–3 klatkach obok siebie — szybciej niż renderować w Resolve.
- Archiwum SD (720×576, SAR ≠ 1): najpierw `scale=iw*sar:ih,setsar=1`. **Nie powiększaj na cały kadr HD** — rozmyte. Daj okno ~1,6× SD (`scale=W*0.62`) na rozmytym, przyciemnionym tle z tego samego obrazu (`gblur=50, eq=brightness=-0.28`), lekki `unsharp` i ziarno.
- Wypalone napisy w archiwum (np. RTVi): przytnij dolne ~26% (`crop=iw*0.94:ih*0.71:iw*0.03:ih*0.03`).
- Bezpieczna pętla korekty: odczyt stanu → propozycja jednej konkretnej zmiany → akceptacja Dimy → kopia → jedna zmiana → eksport klatki + skopy przed/po → porównanie → zostaw lub cofnij.

## Native multicam (Resolve 21.1)

- API: `MediaPool.CreateMulticamClip(clips, MulticamOptions)`, `TimelineItem.PerformMulticamSmartSwitch(...)`, `TimelineItem.FlattenMulticam(gradeOption)`; MCP v4.15.2 ma `create_multicam_clip` i `flatten_multicam`. Starsze zdania w dokumentacji MCP „API nie tworzy multicamu" są nieaktualne.
- **Przetestowane lokalnie** (No More Blues, 09.11, osobny timeline `NATIVE MULTICAM LAB … UNGRADED`): B wyrównany wcześniej przez stream copy od zmierzonej klatki (bez rekompresji, pierwsza klatka identyczna co do bajtu), potem `CreateMulticamClip` z synchronizacją IN → klip `Type=Multicam`, na timeline jeden element wideo + ciągły master WAV na osobnej ścieżce, marker końca pokrycia B. Oryginalny timeline nietknięty, `SaveProject` nie wywołany (autosave Resolve nie audytowany).
- **Co to jest montaż multicam:** wszystkie elementy wideo na V1 wskazują **jeden** klip `Type=Multicam` w puli, cięcia = zmiana kąta, na V2 nie ma wstawek innej kamery. Sam `Type=Multicam` nic nie dowodzi: 09.11 jako „multicam" oddano stary stacked edit (A na V1, B na V2) z każdym plikiem owiniętym w osobny multicam. Kontrola po każdej budowie (tylko odczyt): jeden `mpid` na V1, oczekiwana liczba elementów, V2 pusta, klatki kontrolne każdego kąta. Nie przechodzi → nie nazywaj tego multicamem.
- **API nie ma settera kąta** (09.11: brak w `.pyi`, MCP samuelgursky, emircbngl, DigitalWorkflowCompany, Positronikal). Dwie przetestowane drogi (21.1.1, 09.11):
  1. **Budowa z listy cięć przez DRT** — bez UI. `Timeline.Export(path, EXPORT_DRT, EXPORT_NONE)` timeline'u z jednym elementem multicam → `scripts/drt_cuts.py SRC.drt OUT.drt NAZWA "A:0-144,B:144-295,…"` (klatki timeline'u, `[start,end)`, ciągłe) → `MediaPool.ImportTimelineFromFile(OUT.drt)`. W DRT kąt elementu to napis `Camera 1`/`Camera 2` w `FieldsBlob` (skrypt: `A`→1, `B`→2 — sprawdź kolejność kątów w danym klipie) + `Start/Duration/In`. Wynik: nowy timeline nazwany jak **plik** (`timelineName` nie działa dla DRT), elementy wskazują **istniejący** klip multicam w puli (bez duplikatu), cięcia dokładnie wg listy, klatki A/B identyczne co do piksela z referencją. DRT to format wewnętrzny, nieudokumentowany — po aktualizacji Resolve powtórz test 5 cięć. Każdy import = nowy timeline, nie edycja istniejącego.
  2. **Przełączenie w miejscu przez menu** (System Events; to samo robi `menu_pick` z emircbngl/davinci-resolve-mcp-free): `SetCurrentTimecode` do środka kawałka → `Edit › Deselect All` → `Clip › Multicam Switch › Switch to Angle N`. Bez zaznaczenia przełącza **tylko element pod playheadem**, sąsiedzi bez zmian. `Clip › Multicam Cut` był wyszarzony. Wymaga Accessibility i wyciąga Resolve na wierzch — za zgodą Dimy. Odczytaj nazwy elementów po każdym przełączeniu. Droga do poprawek po ręcznej edycji Dimy (DRT tworzyłby nowy timeline).
- **Grade siedzi na zewnętrznym elemencie multicam, nie na kącie.** Po budowie/przełączeniu kopiuj grade per kąt: `źródłoA.CopyGrades([elementy A])`, `źródłoB.CopyGrades([elementy B])` (źródła = elementy zatwierdzonego timeline'u Dimy; działa między timeline'ami). Po zmianie kąta skopiuj ponownie. 09.11: A identyczne co do piksela z `FULL PERFORMANCE`; B (z OFX Gamut Mapping) MAE 1,1 / max 11, równomierne lekkie ocieplenie na tej samej klatce (±1 klatka daje MAE 3–4) — przyczyna niewyjaśniona.
- **Grade-wzorce Dimy, propagowane przez AI.** Krzywych (Hue vs Sat itd.) API nie ustawia, więc AI nie *tworzy* takiej korekcji — Dima robi ją ręcznie na jednym reprezentatywnym kawałku na kąt, AI: (1) czyta `GetToolsInNode` wszystkich elementów, żeby nie nadpisać innych ręcznych zmian; (2) eksportuje klatkę (środek) każdego elementu; (3) `wzorzec.CopyGrades([elementy tego kąta])`; (4) eksportuje ponownie i mierzy `scripts/vector_stats.py PRZED PO` (p99 chroma, % poza promieniem 0,30, nasycenie niebieskiego/ciepłych); (5) pokazuje arkusz przed/po. Kawałek, na którym wzorzec pogarsza wynik (np. gasi ciepło skóry), wraca do poprzedniego źródła grade'u. 09.11 No More Blues: wzorzec B „trzyma wektoroskop" (Hue vs Sat w dół na niebieskim/fiolecie) → p99 ~34→~29, poza 0,30: 2–6 %→0–1 %, ciepłe −0,7; wzorzec A „dodaje żaru" (Hue vs Sat w górę na żółto-pomarańczowym) → ciepłe +4…6, reszta bez zmian. To proxy 8 bit; ocenę obrazu daje Dima.
- **Wybór ujęć B na koncercie:** arkusz klatek co 2 s + energia ruchu na sekundę (średnia |Δ| na 36×64 gray); ruchy kamery B zasłaniaj kątem A, cięcia przyciągaj do beatów mastera (madmom, `~/.venvs/madmom`). Plan v1 i treść B: `references/project-no-more-blues.md`.
- **Nietestowane:** SmartSwitch (przełącza wg mówiącego — to nie analiza fraz muzycznych), grade wewnątrz kątów, routing audio. Flatten na kopii zadziałał u Hermesa (`FINAL_CHECKS.json`, 09.11). Nie zastępuj zatwierdzonego montażu Dimy laboratoryjnym.
- `MediaPoolItem.GetTimeline()` na klipie multicam zwraca pusty wynik (obserwacja Hermesa, 21.1.1) — zgodnie z `.pyi`, które obiecuje timeline tylko dla *timeline clip*. Wnętrza multicamu (kątów) nie czytaj tą drogą; to nie znaczy, że multicam nie działa.
- Nie podawaj kadrów kamery poza jej synchronicznym pokryciem jako synchronicznego wykonania; nie rób „fałszywego multicamu" cyfrowym zoomem.

## Skopy

- W zakwalifikowanej ścieżce scripting/MCP v4.15.2 **nie potwierdzono** liczbowego feedu natywnych waveform/parade/vectorscope; wbudowany MCP 21.1 pozostaje nietestowany. Są dwie drogi: zrzut UI skopów (Computer Use — wymaga działającego `cua-driver`) albo własne skopy z wyeksportowanej klatki.
- `Project.ExportCurrentFrameAsStill(path)` eksportuje przetworzoną klatkę; format wg rozszerzenia (przetestowane 09.11): **PNG** 8 bit · **TIFF** rgb48 · **DPX** 10 bit. W zbadanej klatce (źródło ProRes 10 bit) TIFF i DPX niosły realne **10 bit** (1024 poziomy; PNG = TIFF>>8, DPX = TIFF>>6) — `HERMES_v1.2_REVIEW_CHECKS.json`; nie uogólniaj na wszystkie efekty/projekty. Do pomiarów eksportuj TIFF/DPX.
- **`scripts/proxy_scopes.py`** (numpy/Pillow z venv Hermesa):
  `~/.hermes/hermes-agent/venv/bin/python ~/Knowledge/_skills/davinci-resolve/scripts/proxy_scopes.py klatka.png --space display-rec709 --output-prefix out` → parade RGB, histogram, CbCr + JSON. `--rect x,y,w,h` (ułamki) = ręczny region, np. twarz. `--self-test` sprawdza arytmetykę. Skrypt liczy **tylko 8 bit** (TIFF16/DPX nieobsługiwane — nie przycinaj ich po cichu do 8 bit); `--space` to deklaracja wywołującego (log/HDR odrzucane), kodowania nie wykrywa.
- To przybliżenie, nie natywne skopy: nie daje IRE, legalności broadcast, HDR ani dowodu przepalenia w kamerze. Wektoroskop całej klatki na koncercie pokazuje lampy i kurtyny, nie skórę. Ścieżka pliku ≠ obejrzany obraz.

## Audio w montażu

- Każdą wypowiedź normalizuj osobno: `loudnorm=I=-16:TP=-1.5:LRA=11` (cel −16 LUFS, cały zwiastun wychodzi ~−14 LUFS — tyle, ile normalizuje YouTube).
- **Jeśli rozmówca „brzmi ciszej" mimo tych samych LUFS — sprawdź szum tła:** `astats` → `Noise floor dB`. Szum pomieszczenia (u jednego rozmówcy −28 dB wobec −75 dB u drugiego) jest wliczany do głośności, więc sam głos ląduje niżej. Leczenie: `highpass=f=90,afftdn=nr=14:nf=-35,equalizer=f=3000:t=q:w=1:g=3` przed loudnorm i `volume=+2…3dB` po nim — ostateczna ocena na słuch Dimy.
- Weryfikacja: `ebur128` dla każdego okna osobno na **miksie** i na **ścieżce samej mowy** — różnica pokazuje, ile dokłada podkład muzyczny. Mierz głośność **po** finalnym mapowaniu kanałów i kodowaniu (mono skopiowane na oba kanały daje ok. +3 LU).
- Cięcia w mowie: transkrypcja whisper ma zgrubne czasy słów; dokładny punkt cięcia znajdź krótką transkrypcją okna + RMS (szukaj ciszy przed „eee"). Niski RMS to nie dowód bezpiecznego cięcia — nie obcinaj cichych spółgłosek; ostatecznie decyduje słuch.

## Koncerty: kamery + osobny WAV (synchronizacja i delivery)

- Zbadaj dokładny plik: czas trwania, kolejność strumieni, sample rate/bit depth, rotacja, tagi koloru, **rzeczywisty** frame rate. FPS w metadanych to nie dowód stałych timestampów (telefony = VFR) — nie przemianowuj VFR na CFR bez konwersji i sprawdzenia długości.
- Przesunięcie kamera↔WAV **mierz** w kilku oknach audio i zapisz znak opóźnienia; równe długości nie dowodzą synchronizacji. W ffmpeg `-itsoffset L` przed wejściem WAV opóźnia WAV.
- Master WAV ciągły przez wszystkie cięcia obrazu; ścieżki kamer tylko do synchronizacji, nie w miksie. Mapuj audio jawnie (`-map`), bo automatyczny wybór może wziąć dźwięk z kamery.
- Master muzyczny (np. ~−7,7 LUFS) to już gotowy master — nie nakładaj na niego presetów mowy (loudnorm −16, denoise).
- Dane konkretnego projektu (znak i wartość opóźnienia, pokrycie kamer, ustawienia Gamut Mapping, rytm cięć): [references/project-no-more-blues.md](references/project-no-more-blues.md).
- Pionowe wersje społecznościowe: H.264/yuv420p + AAC stereo + `+faststart`, 1080×1920; fps dobieraj ze źródła, nie zawsze 25.

## Napisy, plansze, miniatury

- Napisy i plansze końcowe: plik ASS (`subtitles=filename=...`), styl `SF Pro Display`; imię zawsze **„Dima Gorelik" bez odmiany**.
- ASS bez `PlayResX/PlayResY` odtwarzacze traktują jako 384×288 → gigantyczny tekst. Dla 1080p: `PlayResX: 1920`, `PlayResY: 1080`, Arial 54, obrys 2,5, cień 1, marginesy 160/160/60.
- `drawtext` z `font='Helvetica Neue:style=Bold'` cicho spada do nie-pogrubionego fontu — używaj `fontfile='/System/Library/Fonts/Supplemental/Arial Bold.ttf'`.
- Miniatura YouTube 1280×720: porównanie „wtedy / dziś" (klatka z archiwum + portret) mocno działa. Polecenie do odtworzenia trzymaj obok w repo.
- Pionowa plansza 1080×1920: długie linie `CardSmall` się zawijają — skróć tekst albo zwiększ odstęp.
- Nakładki z alfą: ffmpeg QTRLE/argb → V2 w Resolve działa (render pokazuje nakładkę tylko w jej prostokącie); interpretacja alfy i jakość krawędzi — nieprzetestowane.

## Kadr 9:16 — „skaczące klatki"

- Skok kadru w punktach kontrolnych stawiaj **dokładnie na cięciu źródła** (`scdet=threshold=8` na fragmencie), nie „na oko" — różnica 0,08 s = 1–2 klatki złego kadru, widoczne jako podskok.
- Auto-kadr (`smartcrop.py`): w ujęciu jedna prosta (polyfit) z limitem prędkości, nie średnia ruchoma — ta „pływała" tam i z powrotem.
- Kontrola: różnice klatek + `phaseCorrelate` (dwa duże skoki pod rząd = kadr przestawiony obok cięcia) i arkusz klatek wokół każdego cięcia.

## Weryfikacja przed oddaniem

1. Klatka z planszy końcowej i z każdej twarzy (`-ss T -frames:v 1`), obejrzana.
2. `ebur128` całości i odcinków; `TP ≤ −1 dBTP`.
3. `ffprobe` — długość, liczba klatek, fps, `yuv420p`, AAC, `+faststart`.
4. Wersjonuj pliki wyjściowe (`_v8`, `_v9`), nie nadpisuj zatwierdzonej wersji.
5. Liczby (QA pikseli, LUFS) nie zastępują akceptacji Dimy — obraz i słuch ocenia on. Agent może przygotować shortlistę muzyki na wyłączonych ścieżkach do odsłuchu, ale nie twierdzi, że ją ocenił.

Praktyki z badań YouTube/Reddit i z zewnętrznych skills (co przyjęte, co odrzucone, co do testu): [references/research-workflows.md](references/research-workflows.md).

## Final Cut Pro

- M4 ma FCP 12.2; starsze projekty żyją na laptopie Big Sur (FCPXML 1.8).
- Przepływ: FCP → `File → Export XML…` do `Video Production/projects/` → edycja przez MCP `fcpxml` (15 narzędzi, `fcp-mcp-server==0.27.2` przez `uvx`) → import z powrotem.
- MCP widzi tylko katalogi z `FCP_PROJECTS_DIRS`: `Video Production/projects` i `/Volumes/Project 1/Video`.
- Dokumentacja formatu: `Video Production/docs/fcpxml-reference.md`, multicam/fps: `docs/fcpxml-multicam-framerate-conversion.md`.

## Instalacja MCP (Claude Code i Hermes)

Patrz `references/install-mcp.md` — gotowe polecenia dla obu klientów i smoke test.
