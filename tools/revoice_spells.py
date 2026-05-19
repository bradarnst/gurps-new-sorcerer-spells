from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
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
DEFAULT_BASE_URL = os.environ.get("LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.kilo.ai/api/gateway"
API_KEY_ENV_CANDIDATES = ("LLM_API_KEY", "KILO_API_KEY", "OPENAI_API_KEY")
FINAL_COUNSEL_FIELD = "archmagisters_counsel"
LEGACY_COUNSEL_FIELD = "use_example"
MAX_API_RETRIES = 6
INITIAL_RETRY_DELAY_SECONDS = 15.0
MAX_RETRY_DELAY_SECONDS = 120.0
DEFAULT_CHECKPOINT_INTERVAL = 25

SYSTEM_INSTRUCTIONS = """You are rewriting GURPS Sorcery spell records.

Your job for each spell is to return exactly two fields:
- description
- archmagisters_counsel

Hard requirements:
- Preserve the spell's existing game mechanics and factual constraints.
- Do not invent new mechanics, modifiers, durations, resistances, or side effects.
- Keep the description concise, precise, and useful at the table.
- Keep the archmagisters_counsel practical and specific, as a brief example of how a player or NPC might use the spell in play.
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
            "archmagisters_counsel": {"type": "string"},
        },
        "required": ["description", FINAL_COUNSEL_FIELD],
    },
}


@dataclass(frozen=True)
class ScriptConfig:
    input_path: Path
    output_path: Path
    report_path: Path
    progress_path: Path
    prompt_file: Path
    model: str
    base_url: str
    api_key: str
    api_key_env: str
    checkpoint_interval: int
    fresh: bool


class GenerationError(RuntimeError):
    pass


def parse_args() -> ScriptConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Rewrite final spell descriptions and fill archmagisters_counsel fields using an "
            "OpenAI-compatible LLM API. Saves progress periodically and resumes automatically."
        )
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input spell dataset JSON path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output spell dataset JSON path.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output report JSON path.")
    parser.add_argument("--progress-file", default=None, help="Progress checkpoint JSON path. Defaults to <output>.progress.json.")
    parser.add_argument("--checkpoint-interval", type=int, default=DEFAULT_CHECKPOINT_INTERVAL, help=f"Save progress every N completed spells. Defaults to {DEFAULT_CHECKPOINT_INTERVAL}.")
    parser.add_argument("--fresh", action="store_true", help="Ignore any existing progress file and start from the beginning.")
    parser.add_argument("--prompt-file", required=True, help="Path to the user's full voice/style prompt.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name for the target provider. Defaults to LLM_MODEL, OPENAI_MODEL, or gpt-5.4.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL. Defaults to LLM_BASE_URL, OPENAI_BASE_URL, or https://api.kilo.ai/api/gateway.")
    parser.add_argument("--api-key", default=None, help="API key. Defaults to LLM_API_KEY, KILO_API_KEY, or OPENAI_API_KEY environment variable.")
    args = parser.parse_args()

    if args.checkpoint_interval <= 0:
        raise SystemExit("--checkpoint-interval must be a positive integer.")

    output_path = Path(args.output).resolve()
    progress_path = Path(args.progress_file).resolve() if args.progress_file else default_progress_path(output_path)
    base_url = (args.base_url or DEFAULT_BASE_URL).rstrip("/")
    api_key_env, api_key = resolve_api_key(override_key=args.api_key)

    return ScriptConfig(
        input_path=Path(args.input).resolve(),
        output_path=output_path,
        report_path=Path(args.report).resolve(),
        progress_path=progress_path,
        prompt_file=Path(args.prompt_file).resolve(),
        model=args.model,
        base_url=base_url,
        api_key=api_key,
        api_key_env=api_key_env,
        checkpoint_interval=args.checkpoint_interval,
        fresh=args.fresh,
    )


def default_progress_path(output_path: Path) -> Path:
    return output_path.with_suffix(".progress.json")


def resolve_api_key(override_key: str | None = None) -> tuple[str, str]:
    if override_key:
        return "--api-key", override_key
    for env_name in API_KEY_ENV_CANDIDATES:
        value = os.environ.get(env_name, "").strip()
        if value:
            return env_name, value
    env_list = ", ".join(API_KEY_ENV_CANDIDATES)
    raise SystemExit(f"One of these environment variables is required, or pass --api-key: {env_list}")


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
    for attempt in range(1, MAX_API_RETRIES + 1):
        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            if should_retry_http_error(exc.code, attempt):
                delay = compute_retry_delay_seconds(exc.headers.get("Retry-After"), attempt)
                print(
                    f"HTTP {exc.code} from model API on attempt {attempt}/{MAX_API_RETRIES}; retrying in {delay:.1f}s.",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise GenerationError(build_http_error_message(exc.code, details)) from exc
        except error.URLError as exc:
            if attempt < MAX_API_RETRIES:
                delay = compute_retry_delay_seconds(None, attempt)
                print(
                    f"Network error from model API on attempt {attempt}/{MAX_API_RETRIES}: {exc.reason}; retrying in {delay:.1f}s.",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise GenerationError(f"API request failed: {exc.reason}") from exc

    raise GenerationError("API request exhausted all retry attempts.")


def should_retry_http_error(status_code: int, attempt: int) -> bool:
    if attempt >= MAX_API_RETRIES:
        return False
    return status_code == 429 or 500 <= status_code < 600


def compute_retry_delay_seconds(retry_after_header: str | None, attempt: int) -> float:
    if retry_after_header:
        try:
            return min(float(retry_after_header), MAX_RETRY_DELAY_SECONDS)
        except ValueError:
            pass
    return min(INITIAL_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)), MAX_RETRY_DELAY_SECONDS)


def build_http_error_message(status_code: int, details: str) -> str:
    base_message = f"API request failed with HTTP {status_code}: {details}"
    if status_code == 429 and "[BYOK]" in details:
        return (
            f"{base_message}\n"
            "The Kilo Gateway is routing this provider through your BYOK key, and that provider key hit its own rate limit. "
            "If you want the run to use Kilo credits instead of your personal provider limits, remove or disable that provider's BYOK key in the Kilo dashboard before retrying."
        )
    return base_message


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
    archmagisters_counsel = payload.get(FINAL_COUNSEL_FIELD)
    if not isinstance(description, str) or not description.strip():
        raise GenerationError(f"{spell_name}: description was missing or blank.")
    if not isinstance(archmagisters_counsel, str) or not archmagisters_counsel.strip():
        raise GenerationError(f"{spell_name}: {FINAL_COUNSEL_FIELD} was missing or blank.")
    return normalize_ws(description), normalize_ws(archmagisters_counsel)


def rewrite_spell(spell: dict[str, Any], style_prompt: str, config: ScriptConfig) -> dict[str, Any]:
    user_prompt = build_user_prompt(spell, style_prompt)
    api_response = post_chat_completion(config, SYSTEM_INSTRUCTIONS, user_prompt)
    generated = extract_response_json(api_response)
    description, archmagisters_counsel = validate_generated_fields(spell["spell_name"], generated)
    updated_spell = dict(spell)
    updated_spell["description"] = description
    updated_spell.pop(LEGACY_COUNSEL_FIELD, None)
    updated_spell[FINAL_COUNSEL_FIELD] = archmagisters_counsel
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
    metadata.pop("resume_state", None)
    metadata.pop("progress_status", None)
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


def build_progress_payload(input_payload: dict[str, Any], working_spells: list[dict[str, Any]], config: ScriptConfig, completed_count: int) -> dict[str, Any]:
    metadata = dict(input_payload.get("metadata", {}))
    metadata["source_file"] = str(config.input_path.name)
    metadata["progress_status"] = "in_progress"
    metadata["voice_model"] = config.model
    metadata["voice_prompt_file"] = str(config.prompt_file)
    metadata["resume_state"] = {
        "input_file": str(config.input_path),
        "progress_file": str(config.progress_path),
        "model": config.model,
        "prompt_file": str(config.prompt_file),
        "checkpoint_interval": config.checkpoint_interval,
        "completed_count": completed_count,
        "total_count": len(working_spells),
        "updated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    return {
        "metadata": metadata,
        "spells": working_spells,
    }


def build_report(
    config: ScriptConfig,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    backups: dict[str, str | None],
    resumed_from_progress: bool,
) -> dict[str, Any]:
    return {
        "input_file": str(config.input_path),
        "output_file": str(config.output_path),
        "report_file": str(config.report_path),
        "progress_file": str(config.progress_path),
        "prompt_file": str(config.prompt_file),
        "model": config.model,
        "base_url": config.base_url,
        "api_key_env": config.api_key_env,
        "checkpoint_interval": config.checkpoint_interval,
        "resumed_from_progress": resumed_from_progress,
        "source_total_spells": input_payload.get("metadata", {}).get("source_total_spells"),
        "processed_count": len(output_payload["spells"]),
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "backups": backups,
    }


def validate_output_spells(spells: list[dict[str, Any]]) -> None:
    for spell in spells:
        if not isinstance(spell.get("description"), str) or not spell["description"].strip():
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' has a blank description after rewriting.")
        if not isinstance(spell.get(FINAL_COUNSEL_FIELD), str) or not spell[FINAL_COUNSEL_FIELD].strip():
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' has a blank {FINAL_COUNSEL_FIELD} after rewriting.")


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
        "source_lineage",
    }
    for spell in spells:
        missing = sorted(required_keys - set(spell))
        if missing:
            raise SystemExit(f"Spell '{spell.get('spell_name', '<unknown>')}' is missing keys: {missing}")
        if FINAL_COUNSEL_FIELD not in spell and LEGACY_COUNSEL_FIELD not in spell:
            raise SystemExit(
                f"Spell '{spell.get('spell_name', '<unknown>')}' is missing both {FINAL_COUNSEL_FIELD!r} and {LEGACY_COUNSEL_FIELD!r}."
            )
    return spells


def infer_completed_count(spells: list[dict[str, Any]]) -> int:
    completed_count = 0
    for spell in spells:
        if isinstance(spell.get(FINAL_COUNSEL_FIELD), str) and spell[FINAL_COUNSEL_FIELD].strip():
            completed_count += 1
            continue
        break
    return completed_count


def load_working_spells(source_spells: list[dict[str, Any]], config: ScriptConfig) -> tuple[list[dict[str, Any]], int, bool]:
    if config.fresh or not config.progress_path.exists():
        return [dict(spell) for spell in source_spells], 0, False

    progress_payload = read_json(config.progress_path)
    progress_spells = progress_payload.get("spells")
    if not isinstance(progress_spells, list) or len(progress_spells) != len(source_spells):
        raise SystemExit(
            f"Progress file {config.progress_path} is invalid or does not match the input spell count. Use --fresh to start over."
        )

    resume_state = progress_payload.get("metadata", {}).get("resume_state", {})
    validate_resume_state(config, resume_state, len(source_spells))

    completed_count = resume_state.get("completed_count")
    if not isinstance(completed_count, int) or not (0 <= completed_count <= len(progress_spells)):
        completed_count = infer_completed_count(progress_spells)

    print(
        f"Resuming from {config.progress_path.name}: {completed_count}/{len(progress_spells)} spells already saved.",
        file=sys.stderr,
    )
    return progress_spells, completed_count, True


def validate_resume_state(config: ScriptConfig, resume_state: Any, total_count: int) -> None:
    if not isinstance(resume_state, dict):
        return

    expected_input = str(config.input_path)
    expected_prompt = str(config.prompt_file)
    if resume_state.get("input_file") not in (None, expected_input):
        raise SystemExit(
            f"Progress file {config.progress_path} was created for a different input file. Use --fresh to start over."
        )
    if resume_state.get("prompt_file") not in (None, expected_prompt):
        raise SystemExit(
            f"Progress file {config.progress_path} was created with a different prompt file. Use --fresh to start over."
        )
    if resume_state.get("model") not in (None, config.model):
        raise SystemExit(
            f"Progress file {config.progress_path} was created with a different model. Use --fresh to start over."
        )
    if resume_state.get("total_count") not in (None, total_count):
        raise SystemExit(
            f"Progress file {config.progress_path} does not match the current spell count. Use --fresh to start over."
        )


def write_progress_checkpoint(
    input_payload: dict[str, Any],
    working_spells: list[dict[str, Any]],
    config: ScriptConfig,
    completed_count: int,
) -> None:
    progress_payload = build_progress_payload(input_payload, working_spells, config, completed_count)
    atomic_write_json(config.progress_path, progress_payload)
    print(
        f"Checkpoint saved to {config.progress_path.name}: {completed_count}/{len(working_spells)} spells.",
        file=sys.stderr,
    )


def cleanup_progress_file(progress_path: Path) -> None:
    if progress_path.exists():
        progress_path.unlink()


def main() -> None:
    config = parse_args()
    input_payload = read_json(config.input_path)
    style_prompt = read_text(config.prompt_file).strip()
    if not style_prompt:
        raise SystemExit(f"Prompt file is blank: {config.prompt_file}")

    source_spells = validate_input_payload(input_payload)
    working_spells, completed_count, resumed_from_progress = load_working_spells(source_spells, config)
    last_checkpoint_count = completed_count

    if completed_count == len(source_spells):
        print("Progress file already contains all spells. Finalizing output.", file=sys.stderr)

    for index in range(completed_count, len(source_spells)):
        spell = working_spells[index]
        try:
            working_spells[index] = rewrite_spell(spell, style_prompt, config)
        except GenerationError as exc:
            if completed_count > last_checkpoint_count:
                write_progress_checkpoint(input_payload, working_spells, config, completed_count)
            raise SystemExit(f"Failed on spell {index + 1}/{len(source_spells)} '{spell['spell_name']}': {exc}") from exc

        completed_count = index + 1
        if completed_count % config.checkpoint_interval == 0 or completed_count == len(source_spells):
            write_progress_checkpoint(input_payload, working_spells, config, completed_count)
            last_checkpoint_count = completed_count
            print(f"Processed {completed_count}/{len(source_spells)} spells", file=sys.stderr)

    validate_output_spells(working_spells)
    output_payload = build_output_dataset(input_payload, working_spells, config)
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
        resumed_from_progress=resumed_from_progress,
    )

    atomic_write_json(config.output_path, output_payload)
    atomic_write_json(config.report_path, report_payload)
    cleanup_progress_file(config.progress_path)
    print(f"Completed {len(working_spells)}/{len(working_spells)} spells", file=sys.stderr)


if __name__ == "__main__":
    main()
