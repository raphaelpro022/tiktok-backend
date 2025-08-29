import os
import requests
import time
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN")

def refresh_access_token():
    url = "https://YOUR-VERCEL-APP.vercel.app/api/refresh"
    response = requests.post(url, json={"refresh_token": REFRESH_TOKEN})
    if response.status_code == 200:
        data = response.json()
        os.environ["TIKTOK_ACCESS_TOKEN"] = data["access_token"]
        return data["access_token"]
    else:
        print("Erreur refresh token:", response.text)
        return None

def generate_video(text, filename="output.mp4"):
    bg = ColorClip(size=(720,1280), color=(0,0,0), duration=10)
    txt = TextClip(text, fontsize=50, color='white').set_duration(10).set_position('center')
    final = CompositeVideoClip([bg, txt])
    final.write_videofile(filename, fps=24)

if __name__ == "__main__":
    while True:
        token = os.getenv("TIKTOK_ACCESS_TOKEN") or refresh_access_token()
        generate_video("Vidéo générée automatiquement")
        print("Vidéo générée !")
        time.sleep(3600)
