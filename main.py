import os, random, subprocess, datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import wave

# --- 1. 15 MIN KI AUDIO BANAO (Birds Chirps Jaisi Awaz) ---
def make_birds_audio(filename="birds_15min.wav", duration=900):
    sr = 22050
    total = int(sr * duration)
    audio = np.zeros(total, dtype=np.float32)
    # Halki hawa + chirps
    for _ in range(1200):
        start = random.randint(0, total-2000)
        freq = random.randint(2000, 5000)
        length = random.randint(800, 2500)
        t = np.arange(length) / sr
        chirp = np.sin(2*np.pi*freq*t + 5*np.sin(2*np.pi*20*t)) * np.exp(-t*8)
        end = min(start+length, total)
        audio[start:end] += chirp[:end-start]*0.4
    audio = audio / (np.max(np.abs(audio))+0.01) * 0.8
    audio_int = (audio*32767).astype(np.int16)
    with wave.open(filename,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(audio_int.tobytes())
    return filename

# --- 2. PHOTO BANAO ---
def make_image():
    img = Image.new('RGB', (1280,720), color=(20,60,40))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 70)
        f2 = ImageFont.truetype("DejaVuSans.ttf", 32)
    except:
        f1 = f2 = ImageFont.load_default()
    d.text((80,280), "Birds Sounds Focus", fill=(255,255,255), font=f1)
    d.text((80,380), "8 Hours Relaxing Birds Sounds | Study, Sleep, Focus", fill=(200,255,200), font=f2)
    d.text((80,430), f"{datetime.date.today()}  |  Birds Sounds Focus", fill=(180,180,180), font=f2)
    img.save("bg.jpg")
    return "bg.jpg"

# --- 3. 15 MIN VIDEO BANAO ---
def make_15min():
    audio = make_birds_audio()
    img = make_image()
    subprocess.run(["ffmpeg","-y","-loop","1","-i",img,"-i",audio,"-c:v","libx264","-t","900","-pix_fmt","yuv420p","-c:a","aac","-shortest","part15.mp4"], check=True)
    return "part15.mp4"

# --- 4. 32 BAAR JOR KE 8 GHANTE KARO (Concat - Memory Nahi Lagti) ---
def make_8hours():
    part = make_15min()
    with open("list.txt","w") as f:
        for i in range(32):
            f.write(f"file '{part}'\n")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i","list.txt","-c","copy","final_8hours.mp4"], check=True)
    return "final_8hours.mp4"

# --- 5. YOUTUBE UPLOAD ---
def upload_youtube(video_file):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(None,
        refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get("YOUTUBE_CLIENT_ID"),
        client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET"))
    youtube = build("youtube","v3", credentials=creds)
    today = datetime.date.today().strftime("%d %B %Y")
    title = f"8 Hours Birds Sounds Focus | Relaxing Birds Chirping for Study, Sleep & Focus | {today}"
    desc = "8 hours relaxing birds sounds for study, sleep, focus and meditation. Birds Sounds Focus channel.\n\n#birdssounds #focus #sleep #study #relaxing"
    req = youtube.videos().insert(part="snippet,status",
        body={"snippet":{"title":title,"description":desc,"tags":["birds sounds","focus","sleep","study","relaxing"],"categoryId":"22"},
        "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}},
        media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True))
    res = req.execute()
    print("Uploaded:", res.get("id"))

if __name__ == "__main__":
    video = make_8hours()
    print("8 Hours Video Ban Gayi:", video)
    upload_youtube(video)
