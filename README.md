# Video-Editing

Skill dla agentów AI (Claude Code / Hermes) do pracy z **DaVinci Resolve 21.1** i Final Cut Pro na macOS:
scripting API, MCP, grading (CDL, DRX, przenoszenie grade'ów), native multicam (w tym przełączanie kątów
przez listę cięć DRT — `scripts/drt_cuts.py`), proxy-skopy z eksportowanych klatek (`scripts/proxy_scopes.py`,
`scripts/vector_stats.py`), synchronizacja koncertów z osobnym WAV, napisy i delivery.

- Główny plik: [`davinci-resolve/SKILL.md`](davinci-resolve/SKILL.md)
- Szczegóły testów i źródła: [`davinci-resolve/references/`](davinci-resolve/references/)

Ścieżki w tekście (`/Users/macbook/...`, `/Volumes/...`) dotyczą maszyny autora — dostosuj do swojej.
Twierdzenia oznaczone jako „przetestowane" sprawdzono na Resolve Studio 21.1.1.10 (macOS, M4).
Kanoniczna wersja jest utrzymywana prywatnie; to jest migawka.

## Jak użyć

**Claude Code** (terminal / desktop / IDE):
```bash
git clone https://github.com/gorelik11/Video-Editing.git
cp -R Video-Editing/davinci-resolve ~/.claude/skills/
```
Skill włącza się sam, gdy rozmowa dotyczy Resolve / FCP (albo wpisz `/davinci-resolve`).
Do sterowania Resolve potrzebny jest otwarty Resolve Studio z Preferences → General → External scripting using = **Local**.

**Claude.ai / aplikacja Claude**: spakuj folder `davinci-resolve` do ZIP (folder w środku archiwum, z `SKILL.md`)
→ Settings → Capabilities → Skills → Upload skill. W czacie Claude nie steruje Resolve bezpośrednio —
skill działa jako wiedza (przepisy API, pułapki, skrypty do uruchomienia u siebie).

**Grok** (i inne czaty bez systemu skills): załącz `davinci-resolve/SKILL.md` do rozmowy albo wklej go
jako instrukcje projektu; pliki z `references/` dołączaj, gdy temat ich dotyczy. Skrypty z `scripts/`
uruchamiasz sam lokalnie (Python 3 + numpy/Pillow; `drt_cuts.py` tylko biblioteka standardowa).

Autor: Dima Gorelik
