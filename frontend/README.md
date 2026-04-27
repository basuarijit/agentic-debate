# Frontend

React frontend for the debate application.

Stack:

- React
- npm

## Local Setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the Vite URL shown in the console, usually:

```text
http://localhost:5173
```

The frontend expects the backend API at:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the backend separately before clicking `Start Debate`.
