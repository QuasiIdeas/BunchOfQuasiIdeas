#!/usr/bin/env bash
# Новая опция: --logs path/to/file или --docker api --tail 50
LOG_INPUT=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --logs)   LOG_INPUT="$(cat "$2")"; shift 2 ;;
    --docker) LOG_INPUT="$(docker compose logs "$2" --tail="${3:-100}")"; shift 3 ;;
    *)        echo "Unknown flag $1"; exit 1 ;;
  esac
done

{
  cat "${PROMPTS[@]}"
  if [[ -n "$LOG_INPUT" ]]; then
    echo '```log'
    echo "$LOG_INPUT"
    echo '```'
  fi
} | "$CODEx" -i
