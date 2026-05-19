# Smart Flood Sentinel Frontend

React + Vite dashboard for the Smart Flood Sentinel project.

## Local Run

```cmd
npm install
npm run dev
```

The dashboard reads API data from:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Vercel Deploy

Vercel can host this frontend, but the backend must also be reachable from the internet. Do not use `127.0.0.1` for `VITE_API_BASE_URL` in Vercel.

In Vercel project settings, add:

```env
VITE_API_BASE_URL=https://your-live-backend-url.example.com
```

Build settings:

- Framework preset: `Vite`
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

