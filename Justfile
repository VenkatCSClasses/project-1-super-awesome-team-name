server:
    uv run fastapi run server/server.py --port 8000

server-dev:
    uv run fastapi dev server/server.py --reload --port 8000

cli:
    uv run cli/cli.py --help