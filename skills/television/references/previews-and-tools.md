# Preview recipes and optional tools

Television captures preview stdout and renders ANSI text. On command failure it displays stderr. Use finite, non-interactive commands, force color when useful, and avoid full-screen programs such as `less`, `csvlens`, or `qsv lens` as preview commands.

## Data-type recipes

| Type | Preview command | Requirement |
|---|---|---|
| Text or code | `bat -n --color=always -- '{}'` | `bat` |
| Markdown | `glow -s dark -w 100 '{}'` | `glow` |
| JSON | `jq -C . '{}'` | `jq` |
| YAML, TOML, or XML | `yq -C . '{}'` | `yq` |
| CSV | `mlr --icsv --opprint --barred head -n 100 '{}'` | `mlr` |
| TSV | `mlr --itsv --opprint --barred head -n 100 '{}'` | `mlr` |
| Directory | `eza --tree --level=2 --color=always '{}'` | `eza` |
| Image | `chafa -s 80x40 '{}'` | `chafa` |
| PDF on macOS | `pdftotext -l 2 -layout '{}' - | head -100` | `pdftotext` |
| PDF on Windows | `pdftotext -l 2 -layout '{}' - | Select-Object -First 100` | `pdftotext` |
| Audio or video | `ffprobe -v quiet -print_format json -show_format -show_streams '{}' | jq -C .` | `ffprobe`, `jq` |

For CSV and TSV, use Miller, qsv, xsv, Python's `csv` module, or PowerShell `Import-Csv`. Never split on literal commas or tabs because quoting, embedded delimiters, and multiline cells make that lossy.

True Kitty or Sixel image protocols are not native preview widgets. Prefer Chafa symbol or ANSI output.

## Baseline and enhancements

Television's official baseline channel dependencies are `fd`, `bat`, and `rg`. Add only the tools required by the requested source and preview types.

Recommended macOS set:

```sh
brew install television fd bat ripgrep jq yq eza glow miller qsv chafa poppler ffmpeg
```

Recommended Windows commands:

```powershell
winget install --exact --id alexpasmantier.television
winget install sharkdp.fd
winget install sharkdp.bat
winget install BurntSushi.ripgrep.MSVC
winget install jqlang.jq
winget install MikeFarah.yq
winget install eza-community.eza
winget install charmbracelet.glow
winget install Miller.Miller
winget install Gyan.FFmpeg
scoop install qsv
```

For Windows images, use Chafa's official native archive. For PDF previews, use a Poppler Windows bundle and add the directory containing `pdftotext.exe` to `PATH`.

Primary installation sources:

- [Television](https://alexpasmantier.github.io/television/getting-started/installation/)
- [bat](https://github.com/sharkdp/bat)
- [fd](https://github.com/sharkdp/fd)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [eza](https://github.com/eza-community/eza/blob/main/INSTALL.md)
- [yq](https://github.com/mikefarah/yq)
- [Miller](https://github.com/johnkerl/miller)
- [qsv](https://github.com/dathere/qsv)
- [Glow](https://github.com/charmbracelet/glow)
- [Chafa](https://hpjansson.org/chafa/download/)
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows)
- [FFmpeg](https://ffmpeg.org/download.html)

## Preflight

macOS:

```sh
for tool in tv fd bat rg jq yq eza glow mlr qsv chafa pdftotext ffprobe; do
  command -v "$tool" >/dev/null 2>&1 || printf 'missing: %s\n' "$tool"
done
```

Windows PowerShell:

```powershell
'tv','fd','bat','rg','jq','yq','eza','glow','mlr','qsv','chafa','pdftotext','ffprobe' |
  ForEach-Object { if (-not (Get-Command $_ -ErrorAction SilentlyContinue)) { "missing: $_" } }
```

Declare every command actually invoked by a cable in `metadata.requirements`. If a preferred tool is absent, either generate a documented fallback that preserves the data contract or report the missing tool before launching Television.
