export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (req.method === "POST" && url.pathname === "/fanout") {
      const { task, system, models } = await req.json();

      const calls = models.map(async (model) => {
        try {
          const r = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${env.OPENROUTER_API_KEY}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model,
              messages: [
                { role: "system", content: system || "You are a concise, helpful assistant." },
                { role: "user", content: task }
              ]
            })
          });
          const j = await r.json();
          const content = j?.choices?.[0]?.message?.content ?? "(no content)";
          return { model, content };
        } catch (e) {
          return { model, content: `**ERROR:** ${e}` };
        }
      });

      const results = await Promise.all(calls);
      return new Response(JSON.stringify({ results }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response("ok", { status: 200 });
  }
}
