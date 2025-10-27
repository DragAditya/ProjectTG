# Deploying the Telegram Bot on Render

This guide shows you how to host the Telegram group‑management bot on **Render** using its [Blueprint specification](https://render.com/docs/blueprint-spec). A Render Blueprint is a YAML file named `render.yaml` in the root of your repository; Render reads this file to set up services and environment variables【183252191343802†L170-L175】.

## 1. Repository structure

Your repository should include:

- `api/index.py` – a FastAPI app that initialises the python‑telegram‑bot `Application` and exposes the `/api/webhook` route. It also sets the Telegram webhook during startup using the `lifespan` context manager, following the approach recommended for PTB v20+【746222387682674†L161-L170】.
- `render.yaml` – the blueprint file that tells Render how to build and run your service.
- `requirements.txt` – Python dependencies (`python‑telegram‑bot`, `fastapi`, `uvicorn`, etc.).

## 2. `render.yaml` configuration

Our `render.yaml` defines a **web service** that installs dependencies and runs the ASGI app with Uvicorn. The key fields are:

- `type: web` – indicates a web service.
- `env: python` – selects the Python runtime.
- `buildCommand` – installs dependencies from `requirements.txt`.
- `startCommand` – runs Uvicorn on the port provided by Render. For FastAPI apps, Render recommends `uvicorn <module>:<app> --host 0.0.0.0 --port $PORT`【244954942325985†L170-L190】.
- `envVars` – lists environment variables that Render will prompt you to fill in via the dashboard. Marking a variable with `sync: false` means you supply it at deploy time and it is not stored in the `render.yaml` file【183252191343802†L244-L259】.

Here is the blueprint used in this project (see `render.yaml`):

```yaml
services:
  - type: web
    name: telegram-group-management-bot
    env: python
    plan: free
    buildCommand: pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
    startCommand: uvicorn api.index:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: WEATHER_API_KEY
        sync: false
      - key: TRANSLATION_API_KEY
        sync: false
      - key: DICTIONARY_API_KEY
        sync: false
      - key: WEBHOOK_URL
        sync: false
```

> **Tip:** Render automatically provides a `RENDER_EXTERNAL_URL` environment variable with your app’s URL. Our FastAPI app reads `WEBHOOK_URL`, `VERCEL_URL` or `RENDER_EXTERNAL_URL` and constructs the full webhook URL as `<base_url>/api/webhook`. You can set `WEBHOOK_URL` explicitly, or just rely on `RENDER_EXTERNAL_URL`.

## 3. Deploy on Render

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket).
2. Sign in to [Render](https://render.com/) and click **New Web Service**. Choose **“Deploy from Repo”** and select your repository.
3. Render detects the `render.yaml` file in the root and reads the configuration. Fill in the values for `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, and any other keys marked with `sync: false`.
4. Click **Create Web Service**. Render will install dependencies and start your app using Uvicorn.

Once deployed, Render assigns a URL such as `https://my-bot.onrender.com`. You can verify the deployment by visiting `/` – you should see `{ "status": "ok" }` as a JSON response.

## 4. Configure the Telegram webhook

After your Render service is live, call the Telegram API’s `setWebhook` method to tell Telegram where to send updates. Replace `<token>` with your bot’s token and `<render-url>` with your service’s URL:

```bash
curl "https://api.telegram.org/bot<token>/setWebhook?url=https://<render-url>/api/webhook"
```

Telegram will respond with `{"ok":true,"result":true}` if the webhook is set successfully. Your bot is now ready to respond to messages via Render.
