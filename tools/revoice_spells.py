from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "processed" / "final-spells.json"
DEFAULT_OUTPUT = ROOT / "processed" / "final-spells.json"
DEFAULT_REPORT = ROOT / "processed" / "final-voicing-report.json"
DEFAULT_MODEL = os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-5.4"
DEFAULT_BASE_URL = os.environ.get("LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
API_KEY_ENV_CANDIDATES = ("LLM_API_KEY", "KILO_API_KEY", "OPENAI_API_KEY")

SYSTEM_INSTRUCTIONS = """You are rewriting GURPS Sorcery spell records.

Your job for each spell is to return exactly two fields:
- description
- use_example

Hard requirements:
- Preserve the spell's existing game mechanics and factual constraints.
- Do not invent new mechanics, modifiers, durations, resistances, or side effects.
- Keep the description concise, precise, and useful at the table.
- Keep the use_example practical and specific, as a brief example of how a player or NPC might use the spell in play.
- Do not mention points about the underlying editing task, dataset, JSON, schema, or prompt.
- Do not rename the spell.
- Do not change spell types, keywords, costs, ranges, durations, statistics, or source lineage.
- Return valid JSON matching the requested schema.
"""

OUTPUT_SCHEMA: dict[str, Any] = {
    "name": "spell_rewrite",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "description": {"type": "string"},
            "use_example": {"type": "string"},
        },
        "required": ["description", "use_example"],
    },
}


@dataclass(frozen=True)
class ScriptConfig:
    input_path: Path
    output_path: Path
    report_path: Path
    prompt_file: Path
    model: str
    base_url: str
    api_key: str
    api_key_env: str


class GenerationError(RuntimeError):
    pass


def parse_args() -> ScriptConfig:
    parser = argparse.ArgumentParser(description="Rewrite final spell descriptions and fill use_example fields using an OpenAI-compatible LLM API.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input spell dataset JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output spell dataset JSON path.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output report JSON path.")
    parser.add_argument("--prompt-file", required=True, help="Path to the user's full voice/style prompt.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name for the target provider. Defaults to LLM_MODEL, OPENAI_MODEL, or gpt-5.4.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="OpenAI-compatible API base URL. Defaults to LLM_BASE_URL, OPENAI_BASE_URL, or https://api.openai.com/v1.")
    args = parser.parse_args()

    api_key_env, api_key = resolve_api_key()

    return ScriptConfig(
        input_path=Path(args.input).resolve(),
        output_path=Path(args.output).resolve(),
        report_path=Path(args.report).resolve(),
        prompt_file=Path(args.prompt_file).resolve(),
        model=args.model,
        base_url=args.base_url.rstrip("/"),
        api_key=api_key,
        api_key_env=api_key_env,
    )


def resolve_api_key() -> tuple[str, str]:
    for env_name in API_KEY_ENV_CANDIDATES:
        value = os.environ.get(env_name, "").strip()
        if value:
            return env_name, value
    env_list = ", ".join(API_KEY_ENV_CANDIDATES)
    raise SystemExit(f"One of these environment variables is required: {env_list}")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing file: {path}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def normalize_ws(value: str) -> str:
    return " ".join(value.split())


def build_user_prompt(spell: dict[str, Any], style_prompt: str) -> str:
    spell_input = {
        "spell_name": spell["spell_name"],
        "spell_types": spell["spell_types"],
        "keywords": spell["keywords"],
        "full_cost": spell["full_cost"],
        "casting_roll": spell["casting_roll"],
        "range": spell["range"],
        "duration": spell["duration"],
        "description": spell["description"],
        "statistics": spell["statistics"],
    }
    return (
        "Apply the following voice/style instructions exactly when rewriting the spell record.\n\n"
        f"{style_prompt.strip()}\n\n"
        "Return JSON only.\n\n"
        "Spell input:\n"
        f"{json.dumps(spell_input, indent=2, ensure_ascii=False)}"
    )


def post_chat_completion(config: ScriptConfig, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": OUTPUT_SCHEMA,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{config.base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise GenerationError(f"API request failed with HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise GenerationError(f"API request failed: {exc.reason}") from exc


def extract_response_json(api_response: dict[str, Any]) -> dict[str, Any]:
    choices = api_response.get("choices")
    if not choices:
        raise GenerationError("API response did not include any choices.")

    message = choices[0].get("message", {})
    refusal = message.get("refusal")
    if refusal:
        raise GenerationError(f"Model refused the request: {refusal}")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise GenerationError("API response did not include string JSON content.")

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"Model response was not valid JSON: {content}") from exc


def validate_generated_fields(spell_name: str, payload: dict[str, Any]) -> tuple[str, str]:
    description = payload.get("description")
    use_example = payload.get("use_example")
    if not isinstance(description, str) or not description.strip():
        raise GenerationError(f"{spell_name}: description was missing or blank.")
    if not isinstance(use_example, str) or not use_example.strip():
        raise GenerationError(f"{spell_name}: use_example was missing or blank.")
    return normalize_ws(description), normalize_ws(use_example)


def rewrite_spell(spell: dict[str, Any], style_prompt: str, config: ScriptConfig) -> dict[str, Any]:
    user_prompt = build_user_prompt(spell, style_prompt)
    api_response = post_chat_completion(config, SYSTEM_INSTRUCTIONS, user_prompt)
    generated = extract_response_json(api_response)
    description, use_example = validate_generated_fields(spell["spell_name"], generated)
    updated_spell = dict(spell)
    updated_spell["description"] = description
    updated_spell["use_example"] = use_example
    return updated_spell


def backup_if_exists(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_path = path.with_name(f"{path.stem}.backup-{timestamp}{path.suffix}")
    shutil.copy2(path, backup_path)
    return backup_path


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def build_output_dataset(input_payload: dict[str, Any], updated_spells: list[dict[str, Any]], config: ScriptConfig) -> dict[str, Any]:
    metadata = dict(input_payload.get("metadata", {}))
    metadata["source_file"] = str(config.input_path.name)
    metadata["processed_scope"] = "final"
    metadata["processed_count"] = len(updated_spells)
    metadata["build_timestamp_utc"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    metadata["voice_model"] = config.model
    metadata["voice_prompt_file"] = str(config.prompt_file)
    metadata["voice_pass_completed"] = True
    return {
        "metadata": metadata,
        "spells": updated_spells,
    }


def build_report(config: ScriptConfig, input_payload: dict[str, Any], output_payload: dict[str, Any], backups: dict[str, str | None]) -> dict[str, Any]:
    return {
        "input_file": str(config.input_path),
        "output_file": str(config.output_path),
        "report_file": str(config.report_path),
        "prompt_file": str(config.prompt_file),
        "model": config.model,
        "base_url": config.base_url,
        "api_key_env": config.api_key_env,
        "source_total_spells": input_payload.get("metadata", {}).get("source_total_spells"),
        "processed_count": len(output_payload["spells"]),
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "backups": backups,
    }


def validate_output_spells(spells: list[dict[str, Any]]) -> None:
    for spell in spells:
        if not isinstance(spell.get("description"), str) or not spell["description"].strip():
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' has a blank description after rewriting.")
        if not isinstance(spell.get("use_example"), str) or not spell["use_example"].strip():
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' has a blank use_example after rewriting.")


def validate_input_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    spells = payload.get("spells")
    if not isinstance(spells, list) or not spells:
        raise SystemExit("Input payload must contain a non-empty 'spells' array.")

    required_keys = {
        "spell_id",
        "spell_name",
        "spell_types",
        "keywords",
        "full_cost",
        "casting_roll",
        "range",
        "duration",
        "description",
        "statistics",
        "use_example",
        "source_lineage",
    }
    for spell in spells:
        missing = sorted(required_keys - set(spell))
        if missing:
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' is missing keys: {missing}")
    return spells


def main() -> None:
    config = parse_args()
    input_payload = read_json(config.input_path)
    style_prompt = read_text(config.prompt_file).strip()
    if not style_prompt:
        raise SystemExit(f"Prompt file is blank: {config.prompt_file}")

    source_spells = validate_input_payload(input_payload)
    updated_spells: list[dict[str, Any]] = []

    for index, spell in enumerate(source_spells, start=1):
        try:
            updated_spells.append(rewrite_spell(spell, style_prompt, config))
        except GenerationError as exc:
            raise SystemExit(f"Failed on spell {index}/{len(source_spells)} '{spell['spell_name']}': {exc}") from exc

        if index % 25 == 0 or index == len(source_spells):
            print(f"Processed {index}/{len(source_spells)} spells", file=sys.stderr)

    validate_output_spells(updated_spells)
    output_payload = build_output_dataset(input_payload, updated_spells, config)
    output_backup = backup_if_exists(config.output_path)
    report_backup = backup_if_exists(config.report_path)
    report_payload = build_report(
        config,
        input_payload,
        output_payload,
        {
            "output_backup": str(output_backup) if output_backup else None,
            "report_backup": str(report_backup) if report_backup else None,
        },
    )

    atomic_write_json(config.output_path, output_payload)
    atomic_write_json(config.report_path, report_payload)


if __name__ == "__main__":
    main()
