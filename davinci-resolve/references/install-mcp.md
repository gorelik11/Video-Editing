# Instalacja MCP: DaVinci Resolve i Final Cut Pro (FCPXML)

Stan na 24.10.2026: oba serwery działają w Claude Code (projekt `Video Production`, plik `.mcp.json`) i w Hermes (profil `ai-shorts-production`).

## 1. DaVinci Resolve — `samuelgursky/davinci-resolve-mcp`

Wymagania: DaVinci Resolve **Studio** (darmowa wersja nie ma zewnętrznego API), Preferences → General → External scripting using = **Local**, Resolve otwarty podczas pracy.

```bash
# kod przypięty do tagu, bez install.py (ten skrypt sam edytuje konfiguracje wielu klientów)
git clone https://github.com/samuelgursky/davinci-resolve-mcp ~/projects/davinci-resolve-mcp
git -C ~/projects/davinci-resolve-mcp checkout v4.15.2
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv ~/.venvs/davinci-resolve-mcp
~/.venvs/davinci-resolve-mcp/bin/pip install 'mcp[cli]>=1.30,<2' pyaaf2
```

Zmienne środowiskowe (macOS):

```
RESOLVE_SCRIPT_API=/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting
RESOLVE_SCRIPT_LIB=/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so
PYTHONPATH=/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules
```

Uwagi: serwer sprawdza aktualizacje na api.github.com; embeddingi tylko przez lokalną Ollamę.

## 2. Final Cut Pro — `fcp-mcp-server` (FCPXML)

Nie wymaga instalacji — uruchamiany przez `uvx` z przypiętą wersją:

```
command: /Users/macbook/.local/bin/uvx
args:    fcp-mcp-server==0.27.2
env:     FCP_PROJECTS_DIR=/Volumes/KINGSTON/Video Production/projects
         FCP_PROJECTS_DIRS=/Volumes/KINGSTON/Video Production/projects:/Volumes/Project 1/Video
```

## 3a. Claude Code

Projektowo w `/Volumes/KINGSTON/Video Production/.mcp.json` (już jest):

```json
{ "mcpServers": {
  "fcpxml": { "command": "/Users/macbook/.local/bin/uvx", "args": ["fcp-mcp-server==0.27.2"],
              "env": { "FCP_PROJECTS_DIR": "...", "FCP_PROJECTS_DIRS": "..." } },
  "davinci-resolve": { "command": "/Users/macbook/.venvs/davinci-resolve-mcp/bin/python",
              "args": ["/Users/macbook/projects/davinci-resolve-mcp/src/server.py"],
              "env": { "RESOLVE_SCRIPT_API": "...", "RESOLVE_SCRIPT_LIB": "...", "PYTHONPATH": "..." } } } }
```

Żeby mieć je w innym katalogu: skopiuj ten plik albo użyj `claude mcp add --scope project ...`.

## 3b. Hermes (profil `ai-shorts-production`) — zrobione 24.10.2026

```bash
H=~/.hermes/hermes-agent/venv/bin/hermes
R="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
echo Y | $H -p ai-shorts-production mcp add davinci-resolve \
  --command /Users/macbook/.venvs/davinci-resolve-mcp/bin/python \
  --args /Users/macbook/projects/davinci-resolve-mcp/src/server.py \
  --env "RESOLVE_SCRIPT_API=$R" \
        "RESOLVE_SCRIPT_LIB=/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so" \
        "PYTHONPATH=$R/Modules"
echo Y | $H -p ai-shorts-production mcp add fcpxml \
  --command /Users/macbook/.local/bin/uvx --args fcp-mcp-server==0.27.2 \
  --env "FCP_PROJECTS_DIR=/Volumes/KINGSTON/Video Production/projects" \
        "FCP_PROJECTS_DIRS=/Volumes/KINGSTON/Video Production/projects:/Volumes/Project 1/Video"
$H -p ai-shorts-production mcp list
```

- `hermes mcp add` jest interaktywne (pyta „Enable all N tools?"), stąd `echo Y |`. Przy dodawaniu łączy się z serwerem i wypisuje narzędzia: 37 dla Resolve, 15 dla FCPXML. To jest smoke test.
- Kopia konfiguracji sprzed zmiany: `~/.hermes/profiles/ai-shorts-production/config.yaml.bak-before-video-mcp-20261024`.
- Narzędzia pojawiają się w **nowej** sesji Hermesa.
- Dla innego profilu zmień `-p`; dla profilu domyślnego pomiń `-p`.

## Smoke test bez klienta

```bash
~/.venvs/davinci-resolve-mcp/bin/python -c "import sys; sys.path.append('/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules'); import DaVinciResolveScript as d; r=d.scriptapp('Resolve'); print(r and r.GetProductName(), r and r.GetVersionString())"
```

`None` oznacza, że Resolve jest zamknięty albo External scripting ≠ Local.
