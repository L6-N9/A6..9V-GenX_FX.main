@echo off
echo GenX-FX Quick Start
npm run build
python -m uvicorn api.main:app --port 8081 --reload &
npx serve dist -p 3000
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8081