import os, anyio, json, textwrap, requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# OpenRouter model IDs (edit as needed)
MODELS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4.1",
    "google/gemini-1.5-pro",
]

def clean_prompt(raw_comment, title, body):
    task = raw_comment.replace("/fanout", "", 1).strip()
    return task or f"Task from issue: {title}\n\n{body or ''}"

def openrouter_chat(model, system, user):
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    r = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"]

async def ask_all(system, user):
    async def ask(model):
        try:
            reply = await anyio.to_thread.run_sync(openrouter_chat, model, system, user)
            return model, reply
        except Exception as e:
            return model, f"**ERROR:** {e}"
    return await anyio.gather(*[ask(m) for m in MODELS])

def post_issue_comment(repo, issue_number, token, markdown):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    r = requests.post(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }, json={"body": markdown}, timeout=60)
    r.raise_for_status()

if __name__ == "__main__":
    repo = os.environ["REPO"]
    issue_number = os.environ["ISSUE_NUMBER"]
    gh_token = os.environ["GITHUB_TOKEN"]
    raw = os.environ.get("PROMPT", "")
    title = os.environ.get("TITLE", "")
    body = os.environ.get("BODY", "")
    task = clean_prompt(raw, title, body)

    system = ("You are a specialist LLM for an engineering team. "
              "Be concise; use short bullets; include tiny code blocks only if essential.")

    results = anyio.run(ask_all, system, task)
    parts = [f"### {model}\n{reply}\n" for model, reply in results]
    rollup = "\n---\n".join(parts)

    md = textwrap.dedent(f"""
    **LLM Fanout Results**

    **Task:**
    ```
    {task}
    ```

    {rollup}
    """).strip()

    post_issue_comment(repo, issue_number, gh_token, md)
