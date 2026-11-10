# Praktyki z badań (YouTube, Reddit, zewnętrzne skills) — decyzje

Źródła: `resolve-mcp-control-research-20261102/night-20261104/` (`youtube-novelty-pass/` — 13 transkryptów `<video_id>.json` + `MANIFEST.json`, `EVIDENCE_CARDS.json`, `REVIEW.json`; wcześniejszy osobny etap `youtube-caption-recovery/`; `reddit-batch-1/run/artifacts/fetch.json`, `reddit-batch-1/apify/*/ITEMS.json`, `CURATED_CONTROLSKILLS.json`); kopie w `resolve-claude-recheck-20261109/02_research_raw_and_reports/` i `05_external_and_adjacent/`. To relacje autorów i dokumentacja, nie nasze testy, jeśli nie zaznaczono inaczej.

Legenda: **PRZYJĘTE** (w SKILL.md) · **REFERENCJA** (użyteczne, sięgnij tutaj) · **ODRZUCONE** · **DO TESTU**.

## YouTube (9 kart, 5 filmów)
| Praktyka | Decyzja |
|---|---|
| Tabela kandydatów source/in/out/zegar/powód/must-or-nice/akceptacja przed montażem | PRZYJĘTE (zasada 8) |
| Przygotowanie w tle ≠ prawo zapisu; plan → zgoda → ponowny odczyt → zapis → odczyt | PRZYJĘTE (zasada 8) |
| Warianty A/B na osobnych timeline (`DuplicateTimeline` daje nowe ID — przetestowane) | PRZYJĘTE; pełna równość grade'ów/Fusion duplikatu — DO TESTU |
| Shortlista muzyki na wyłączonych ścieżkach do odsłuchu przez Dimę | PRZYJĘTE; agent nie „ocenia" muzyki; licencje/zakupy osobno |
| Batch vs mikro-edycja (autor: minuty na trim 1,67 s) | REFERENCJA — drobny trim zostaw Dimie; czasy autora ≠ benchmark M4 |
| Timeout transkrypcji natywnej, zadanie trwało dalej | PRZYJĘTE jako reguła „sprawdź stan przed ponowieniem"; lokalnie DO TESTU |
| Clipto (indeksowanie, wyszukiwanie po osobie/akcji/ubraniu, nazywanie twarzy) | REFERENCJA; niezainstalowane, prywatność niesprawdzona; demo było w Premiere, nie Resolve |
| 2–3 iteracje uwag w strukturze; „done" ≠ widoczny efekt | PRZYJĘTE (weryfikacja) |
| Przypadek CapCut | ODRZUCONE jako dowód możliwości Resolve |

## Reddit (12 wątków / 191 komentarzy; nie reprezentatywna próba)
| Ustalenie | Decyzja |
|---|---|
| Transcript → outline → cytaty-kandydaci → timeline; markery w przebiegach | REFERENCJA dla wywiadów; na koncertach muzyka/przesłuchy psują transkrypt — nie przenosić automatycznie |
| Native 21.1 MCP ≠ zewnętrzny Resolve MCP ≠ Fusion MCP | PRZYJĘTE (mapa kanałów) |
| open-fusion-mcp: 11 narzędzi / 179 operacji, klatki inline, serializowany worker, allowlisty/dry-run; undo batch nie jest transakcją | REFERENCJA — kandydat do audytu, nie instalować |
| Move/trim/transition vs usuń-i-wstaw: sprzeczne relacje o zachowaniu grade/Fusion/retime/audio | PRZYJĘTE jako ostrzeżenie; DO TESTU na kopii |
| Ciche „success" narzędzi, słabe oceny na poziomie klatki | PRZYJĘTE (trzy poziomy dowodu) |
| Embeddings dla binów; stosy lokalnych modeli/Hermes | REFERENCJA — samoopisy bez wersji, nie benchmark |
| stderr natywnego procesu może zablokować potok (Windows) | PRZYJĘTE (czytaj stderr osobno); lokalnie nie odtworzone |

## Zewnętrzne skills (terminalskills/llmbase, alivirgo/Major-AI-Skills)
Przydatne (REFERENCJA, sygnatury sprawdzaj w `DaVinciResolveScript.pyi`):
- Render: `GetRenderFormats`/`GetRenderCodecs`/presety, zachowanie zwróconego ID z `AddRenderJob`, odpytywanie tego ID z `time.sleep`, wypisanie błędu i `CompletionPercentage` — PRZYJĘTE w SKILL.md.
- Biny, metadane, markery + `customData` — przydatne dla długich koncertów/archiwum; DO TESTU.
- Interchange: import/eksport OTIO/AAF/EDL/FCPXML (subtype dla EDL/AAF, `sourceClipsPath`) — DO TESTU na zachowanie (AAF: patrz skill `aaf-reaper-resolve`).
- Render cache / proxy przy TNR, Fusion 3D, braku pamięci GPU — troubleshooting, na M4 nietestowane.
- AI Extras, granica Studio/Free, headless — sprawdzaj kontekstowo; twierdzenia o headless są sprzeczne między skills; nie instaluj Extras automatycznie.
- Color management/CST/tagi eksportu — tylko pod rzeczywisty pipeline projektu, bez sztywnego „Rec.709 2.4 zawsze dla web".

ODRZUCONE (sprawdzone w zapisanych treściach): automatyczne `pm.SaveProject()` po zmianach; pusta pętla `while project.IsRenderingInProgress(): pass`; `GetRenderJobStatus(0)` zamiast zwróconego ID; „sprawdzaj bool każdego settera" (Fusion `SetInput` zwraca `None` przy udanym zapisie); masowe zapisy na wszystkie klipy; upload do chmury domyślnie; TextPlus bez połączenia z `MediaOut` jako dowód widocznego tytułu.
