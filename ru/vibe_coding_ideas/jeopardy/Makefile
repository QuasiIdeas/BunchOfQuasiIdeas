LOG_FILE := .tmp/backend.log

## Собрать последние 100 строк docker-лога API и отправить их в Codex
log:
	@docker compose logs api --tail=100 > $(LOG_FILE)
	@{ \
	  cat $(PROMPTS); \
	  echo '```log'; tail -n 100 $(LOG_FILE); echo '```'; \
	} | $(CODEx) -i
