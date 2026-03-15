run:
	uv run python manage.py runserver 8004

run-celery:
	uv run celery -A bergline worker -l info

run-beat:
	uv run celery -A bergline beat -l info

run-redis:
	redis-server

fetch:
	uv run python manage.py shell -c "from apps.messages.tasks import fetch_and_analyze_messages; fetch_and_analyze_messages()"

migrate:
	uv run python manage.py migrate

nuke:
	rm -f db.sqlite3
	uv run python manage.py migrate

run-bergline:
	trap 'kill 0' EXIT; \
	redis-server --daemonize yes && \
	$(MAKE) run-celery & \
	$(MAKE) run-beat & \
	$(MAKE) run
