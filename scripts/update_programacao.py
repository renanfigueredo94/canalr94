#!/usr/bin/env python3
"""Generate programacao.json from optional guia URLs in canals.json."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ScheduleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[tuple[str, str]] = []
        self._heading: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "h2":
            self._finish_heading()
            self._heading = "h2"
            self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "h2":
            self._finish_heading()

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._heading:
            self._heading_parts.append(text)
        else:
            self.events.append(("text", text))

    def _finish_heading(self) -> None:
        if self._heading:
            title = " ".join(self._heading_parts).strip()
            if title:
                self.events.append((self._heading, title))
        self._heading = None
        self._heading_parts = []


def fetch(url: str) -> str:
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; OnPlayPlus-Guide/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urlopen(request, timeout=15) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def current_and_next(html: str) -> tuple[str, str]:
    parser = ScheduleParser()
    parser.feed(html)
    marker = next((i for i, (kind, text) in enumerate(parser.events)
                   if kind == "text" and "NO AR" in text.upper()), None)
    if marker is None:
        raise ValueError("a página não marcou o programa atual com NO AR")
    current = next((text for kind, text in reversed(parser.events[:marker]) if kind == "h2"), "")
    following = next((text for kind, text in parser.events[marker + 1:] if kind == "h2"), "")
    if not current:
        raise ValueError("não foi possível identificar o programa atual")
    return current, following


def main() -> int:
    root = Path.cwd()
    channel_file = root / "canals.json"
    output_file = root / "programacao.json"
    channels = json.loads(channel_file.read_text(encoding="utf-8-sig"))
    if not isinstance(channels, list):
        raise SystemExit("canals.json deve conter uma lista JSON.")

    records = []
    failures = []
    for channel in channels:
        if not isinstance(channel, dict) or not channel.get("guia"):
            continue
        try:
            now, next_program = current_and_next(fetch(str(channel["guia"])))
            records.append({
                "id": channel.get("id"),
                "canal": channel.get("nome", "Canal"),
                "agora": now,
                "proximo": next_program,
            })
            print(f"OK: {channel.get('nome', channel.get('id'))}: {now}")
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            failures.append(f"{channel.get('nome', channel.get('id'))}: {exc}")
            print(f"AVISO: falha em {channel.get('nome', channel.get('id'))}: {exc}", file=sys.stderr)
        time.sleep(0.25)

    if not records:
        raise SystemExit("Nenhuma programação foi obtida; o arquivo existente foi preservado. "
                         "Confira se os canais possuem a propriedade 'guia' e se as URLs respondem.")

    payload = {
        "atualizadoEm": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "programas": records,
    }
    temp_file = output_file.with_suffix(".json.tmp")
    temp_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_file.replace(output_file)
    print(f"Gerada programação de {len(records)} canal(is) em {output_file.name}.")
    if failures:
        print(f"{len(failures)} canal(is) não foram atualizados; consulte os avisos acima.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
