# JustAsking — Idea Resonator (multi-LLM prompt & synthesis)

Turn one idea into tuned prompts for multiple LLMs (Grok, DeepSeek, Gemini, Claude), optionally through an **information-geometry lens** (Geometric Plasticity / ITPU vibe). Route to your own proxy (safer for API keys), collect answers, and synthesize them into a crisp brief you can export.

**Demo flow**
1) Paste an idea → 2) Generate model-specific prompts → 3) (Optional) call models via your proxy → 4) Auto-synthesize results → 5) Export Markdown.

## Quick start (GitHub Pages)
1. Put `index.html` in repo root.
2. Add an empty `.nojekyll` file (prevents Jekyll interfering with static assets).
3. Commit & push.
4. Settings → Pages → Deploy from branch → `main` / `/root`.
5. Visit: `https://<your-username>.github.io/justasking/`

## Optional: safe API routing
Never expose keys in the browser. Use a tiny proxy (e.g., Cloudflare Worker) from `worker/worker.js`. Put your provider keys in worker env vars, then set the app’s **Proxy base URL**.

Supported in the sample proxy:
- **Grok** (x.ai)
- **DeepSeek**
- **Gemini**
- **Claude**

## Features
- Multi-LLM prompt generator (model-tuned styles).
- “Info-Geometry lens” checklist baked into prompts.
- Mock mode (works with zero keys).
- One-click synthesis + Markdown export.
- Local-only key storage (optional) + BYO proxy.

## Roadmap
- 🔜 Batched prompts, per-provider params.
- 🔜 Save/load sessions (local JSON).
- 🔜 One-click “Create GitHub issue” with the synthesis.

## Contributing
Issues and PRs welcome! Keep PRs small, add a quick before/after note in the description, and test the page locally.

## License
You choose; default is “all rights reserved” for now. If you prefer Apache-2.0 or MIT, add a `LICENSE` file. (I can drop one in if you want Apache again.)

## Multi-LLM Fan-Out (Two Ways)

We support two ways to dispatch a single task to multiple models and collect replies.

### 1) GitHub Actions (issue comment trigger)

- Add a new issue with your task.
- Comment on the issue with:

```
/fanout
```

- A workflow calls multiple models via OpenRouter and posts an aggregated comment.

**Setup**
- Repo secret: `OPENROUTER_API_KEY`

**Files**
- `.github/workflows/fanout.yml`
- `.github/scripts/fanout.py`

### 2) Live UI via Cloudflare Worker Proxy

The site calls a Cloudflare Worker that fans out to several models. This keeps API keys off the client.

**Setup**
- Deploy Worker in `worker/` and set secret:
  - `wrangler secret put OPENROUTER_API_KEY`
- Set the Worker URL in `index.html`:
```html
<script>
  window.JUSTASKING_PROXY = "https://YOUR-WORKER-SUBDOMAIN.workers.dev";
</script>
```

**Files**
- `worker/worker.js`
- `worker/wrangler.toml`
- `index.html` (script block wiring the form to /fanout)

### Changing Models

Edit the model list in:
- `.github/scripts/fanout.py` → `MODELS = [...]`
- `index.html` → `window.JUSTASKING_MODELS = [...]`

### Notes

- No API keys are committed to the repo.
- Errors return as **ERROR:** … per-model so one failure doesn’t block others.

