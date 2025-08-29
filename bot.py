import os, time, json, traceback
import schedule
from datetime import datetime
from services.apify_client import fetch_trending_topics
from services.pexels_client import download_pexels_clip
from services.elevenlabs_client import tts_to_file
from services.tiktok_client import TikTokClient
from video.editor import compose_vertical_video
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    cfg_path = "config.json"
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # fallback to env only
    return {
        "APIFY_TOKEN": os.getenv("APIFY_TOKEN"),
        "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        "ELEVENLABS_VOICE_ID": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        "TIKTOK_CLIENT_KEY": os.getenv("TIKTOK_CLIENT_KEY"),
        "TIKTOK_CLIENT_SECRET": os.getenv("TIKTOK_CLIENT_SECRET"),
        "TIKTOK_REFRESH_TOKEN": os.getenv("TIKTOK_REFRESH_TOKEN"),
        "REDIRECT_URI": os.getenv("REDIRECT_URI"),
        "WORKDIR": os.getenv("WORKDIR", "work"),
        "VIDEO_RESOLUTION": os.getenv("VIDEO_RESOLUTION", "1080x1920"),
        "POST_HOURS_START": int(os.getenv("POST_HOURS_START", "8")),
        "POST_HOURS_END": int(os.getenv("POST_HOURS_END", "18")),
    }

def ensure_dirs(path):
    os.makedirs(path, exist_ok=True)

def create_and_upload_one(cfg):
    try:
        workdir = cfg["WORKDIR"]
        ensure_dirs(workdir)
        topics = fetch_trending_topics(cfg["APIFY_TOKEN"], limit=10)
        topic = topics[0] if topics else {"desc": "Astuce TikTok rapide", "keywords": ["astuce", "tendance"]}
        query = (topic.get("desc") or "tiktok trend").split()[:4]
        query_str = " ".join(query) if query else "tiktok trend"

        print(f"[1/5] 🔎 Tendance choisie: {topic.get('desc', 'N/A')}")
        video_path = download_pexels_clip(cfg["PEXELS_API_KEY"], query_str, os.path.join(workdir, "raw.mp4"))
        if not video_path:
            raise RuntimeError("Aucune vidéo Pexels trouvée")

        print("[2/5] 📝 Génération du script voix...")
        script_text = f"Voici une tendance TikTok : {topic.get('desc', 'une astuce virale')}.\nAbonne-toi pour d'autres idées !"
        audio_path = os.path.join(workdir, "voice.mp3")
        tts_to_file(cfg["ELEVENLABS_API_KEY"], cfg["ELEVENLABS_VOICE_ID"], script_text, audio_path)

        print("[3/5] 🎬 Montage vertical...")
        final_path = os.path.join(workdir, f"final_{int(time.time())}.mp4")
        compose_vertical_video(src_video=video_path,
                               src_audio=audio_path,
                               output_path=final_path,
                               resolution=cfg["VIDEO_RESOLUTION"],
                               caption="Tendance TikTok 🚀")

        print("[4/5] 🔐 Rafraîchissement token TikTok...")
        tk = TikTokClient(cfg["TIKTOK_CLIENT_KEY"], cfg["TIKTOK_CLIENT_SECRET"], cfg["REDIRECT_URI"], cfg["TIKTOK_REFRESH_TOKEN"])
        access_token = tk.refresh_access_token()

        print("[5/5] ⬆️ Upload vers TikTok (brouillon)...")
        resp = tk.upload_video(final_path, access_token)
        print("✅ Upload terminé:", resp)
    except Exception as e:
        print("❌ Erreur:", e)
        traceback.print_exc()

def main():
    cfg = load_config()
    start, end = cfg["POST_HOURS_START"], cfg["POST_HOURS_END"]
    print(f"🤖 Bot démarré. Il créera 1 vidéo/heure de {start}h à {end}h.")
    schedule.every().hour.at(":00").do(create_and_upload_one, cfg=cfg)

    # Lancer immédiatement une première vidéo au démarrage
    create_and_upload_one(cfg)

    while True:
        now = datetime.now()
        if start <= now.hour <= end:
            schedule.run_pending()
        time.sleep(20)

if __name__ == "__main__":
    main()
