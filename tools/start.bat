@echo off
cd /d %~dp0..
start http://localhost:8000
where npx >/dev/null 2>/dev/null && (npx -y http-server -p 8000 -c-1) || (python -m http.server 8000)
