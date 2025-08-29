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
    const { refresh_token } = req.body;

    if (!refresh_token) {
      return res.status(400).json({ error: "Refresh token manquant" });
    }

    const params = new URLSearchParams();
    params.append("client_key", process.env.sbawyevz981byo72o7);
    params.append("client_secret", process.env.CDub1xDKsDQC1qitvJSGBq7wSX4mSVqL);
    params.append("grant_type", "refresh_token");
    params.append("refresh_token", refresh_token);

    const response = await fetch("https://open.tiktokapis.com/v2/oauth/token/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString(),
    });

    const data = await response.json();

    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.status(200).json(data);

  } catch (error) {
    return res.status(500).json({ error: "Erreur serveur", details: error.message });
  }
}
