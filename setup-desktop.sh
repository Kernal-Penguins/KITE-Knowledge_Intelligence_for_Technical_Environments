#!/usr/bin/env bash
# Put KITE on the Desktop and start it. Nothing is installed outside that folder
# except Docker images. Requires Docker Desktop (or Docker Engine) and git.
set -euo pipefail

REPO_URL="https://github.com/Kernal-Penguins/KITE-Knowledge_Intelligence_for_Technical_Environments.git"
BRANCH="cursor/desktop-setup-script-e6d7"

if [[ -d "${HOME}/Desktop" ]]; then
  DESKTOP="${HOME}/Desktop"
elif [[ -n "${USERPROFILE:-}" && -d "${USERPROFILE}/Desktop" ]]; then
  DESKTOP="${USERPROFILE}/Desktop"
else
  DESKTOP="${HOME}/Desktop"
  mkdir -p "${DESKTOP}"
fi
DEST="${DESKTOP}/KITE"

echo "KITE will live only in: ${DEST}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. Install Git, then run this script again." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop, start it, then run this script again." >&2
  echo "https://docs.docker.com/get-docker/" >&2
  exit 1
fi

if [[ -d "${DEST}/.git" ]]; then
  git -C "${DEST}" fetch --depth 1 origin "${BRANCH}"
  git -C "${DEST}" checkout -B "${BRANCH}" FETCH_HEAD
elif [[ ! -f "${DEST}/docker-compose.yml" ]]; then
  rm -rf "${DEST}"
  git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${DEST}"
else
  echo "${DEST} exists but is not a git checkout. Move that folder aside and run this script again." >&2
  exit 1
fi

cd "${DEST}"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

current="$(grep -E '^GEMINI_API_KEY=' .env | head -1 | cut -d= -f2- || true)"
if [[ -z "${current}" ]]; then
  if [[ -n "${GEMINI_API_KEY:-}" ]]; then
    KEY="${GEMINI_API_KEY}"
  else
    echo "The API will not start without a Gemini key."
    echo "Create one at https://aistudio.google.com/apikey"
    read -r -p "Paste GEMINI_API_KEY: " KEY
  fi
  if [[ -z "${KEY}" ]]; then
    echo "No key entered. Edit ${DEST}/.env and run this script again." >&2
    exit 1
  fi
  tmp="$(mktemp)"
  awk -v key="${KEY}" '
    BEGIN { done = 0 }
    /^GEMINI_API_KEY=/ { print "GEMINI_API_KEY=" key; done = 1; next }
    { print }
    END { if (!done) print "GEMINI_API_KEY=" key }
  ' .env > "${tmp}"
  mv "${tmp}" .env
fi

if ! docker info >/dev/null 2>&1; then
  if command -v open >/dev/null 2>&1; then
    open -a Docker >/dev/null 2>&1 || true
  fi
  echo "Waiting for Docker to start..."
  ready=0
  for _ in $(seq 1 60); do
    if docker info >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done
  if [[ "${ready}" -ne 1 ]]; then
    echo "Docker is not running. Start Docker Desktop, then run this script again." >&2
    exit 1
  fi
fi

echo "Building and starting KITE. The first run downloads images and can take several minutes."
docker compose up -d --build

echo "Waiting for the API..."
ok=0
for _ in $(seq 1 90); do
  if curl -sf "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 2
done

echo
echo "Project folder: ${DEST}"
echo "App:            http://localhost:5173"
echo "API docs:       http://localhost:8000/docs"
if [[ "${ok}" -eq 1 ]]; then
  echo "Health:         $(curl -sf http://127.0.0.1:8000/health)"
else
  echo "The API is not healthy yet. Check logs with: cd \"${DEST}\" && docker compose logs backend" >&2
  exit 1
fi

if command -v open >/dev/null 2>&1; then
  open "http://localhost:5173" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:5173" >/dev/null 2>&1 || true
elif command -v cmd.exe >/dev/null 2>&1; then
  cmd.exe /c start http://localhost:5173 >/dev/null 2>&1 || true
fi
