# Deploying the Telegram Bot on Vercel

This guide explains how to deploy your Telegram group‑management bot to **Vercel**. It uses FastAPI and webhook handling so that Telegram can push updates directly to your app. The instructions below summarise the key steps from a detailed blog post on deploying a Telegram bot with FastAPI on Vercel【287173088061026†L149-L165】.

## 1. Prepare your repository

Your repository should contain at least the following files:

- `api/index.py` – this is the FastAPI entry point for Vercel. It creates the bot’s `Application`, registers handlers and services, and exposes a `/api/webhook` route for Telegram updates. Our implementation uses the `lifespan` feature to set the webhook and manage startup/shutdown (see the freeCodeCamp example for an overview【746222387682674†L161-L170】). 
- `vercel.json` – Vercel uses this file to rewrite all incoming routes to `api/index.py`. The blog post emphasises that you must include this file with a rewrite rule such as:

  ```json
  {
    "rewrites": [ { "source": "/(.*)", "destination": "/api/index" } ]
  }
  ```

  Placing `vercel.json` at the root ensures that Vercel always runs your FastAPI function instead of trying to serve static files【287173088061026†L149-L165】.
- `requirements.txt` – include all Python dependencies, including `python-telegram-bot`, `fastapi`, and `uvicorn` at the pinned versions specified in the project.

You can have other files (e.g., `README.md`, test scripts) in the root; they won’t affect deployment【287173088061026†L173-L186】.

## 2. Set environment variables

In the Vercel dashboard, go to your project’s **Settings → Environment Variables** and add the following keys. You do **not** need to commit secrets to your repository:

| Variable | Description |
|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your bot’s token from @BotFather |
| `GEMINI_API_KEY` | API key for Gemini (Google GenAI) |
| `WEATHER_API_KEY` | Weather API key (optional) |
| `TRANSLATION_API_KEY` | Translation API key (optional) |
| `DICTIONARY_API_KEY` | Dictionary API key (optional) |

Additionally, Vercel automatically defines a `VERCEL_URL` variable that contains the public URL of your deployment. Our FastAPI app reads this variable and constructs the webhook URL as `https://<VERCEL_URL>/api/webhook`. If you prefer, you can explicitly set a `WEBHOOK_URL` environment variable instead.

## 3. Deploy to Vercel

1. Push your code to a Git repository.
2. Log in to your Vercel account and click **New Project**.
3. Import your repository and select the correct root folder. Vercel detects the Python runtime automatically.
4. Click **Deploy**. Vercel will install dependencies and deploy your app.

Once deployment completes, Vercel will provide a URL like `https://my‑bot.vercel.app`. The FastAPI app exposes a health check at `/` so you should see `{ "status": "ok" }` when visiting the root.

## 4. Register the webhook

After deploying, tell Telegram where to send updates by calling the `setWebhook` method. Replace `<token>` with your bot’s token and `<your‑vercel‑url>` with the domain from Vercel.

```bash
curl "https://api.telegram.org/bot<token>/setWebhook?url=https://<your‑vercel‑url>/api/webhook"
```

The blog post demonstrates the same step and shows that Telegram will respond with `{"ok":true,"result":true}` if the webhook is set correctly【287173088061026†L285-L299】. Your bot is now ready to receive messages via Vercel!
