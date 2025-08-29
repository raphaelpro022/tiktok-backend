export default async function handler(req, res) {
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Méthode non autorisée" });
  }

  try {
    const { code } = req.body;

    if (!code) {
      return res.status(400).json({ error: "Code TikTok manquant" });
    }

    const params = new URLSearchParams();
    params.append("client_key", process.env.sbawyevz981byo72o7);
    params.append("client_secret", process.env.CDub1xDKsDQC1qitvJSGBq7wSX4mSVqL);
    params.append("code", code);
    params.append("grant_type", "authorization_code");
    params.append("redirect_uri", process.env.https://raphaelpro022.github.io/tiktok-bot/callback.html);

    const response = await fetch("https://open.tiktokapis.com/v2/oauth/token/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString()
    });

    const data = await response.json();

    res.setHeader("Access-Control-Allow-Origin", "*");

    return res.status(200).json(data);

  } catch (error) {
    return res.status(500).json({ error: "Erreur serveur", details: error.message });
  }
}
