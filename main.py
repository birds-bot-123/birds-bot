import random, datetime, requests
import numpy as np
from PIL import Image
from moviepy import ImageClip, AudioClip, concatenate_videoclips
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# --- 1. TITLE + DESCRIPTION - Roz naya ---
TITLES = [
 "8 Hours Relaxing Birds Sounds | Peaceful Forest Morning",
 "8 Hours Birds Chirping in Forest | Relax, Sleep, Focus",
 "8 Hours Calm Birds Sounds | Nature for Deep Sleep",
 "8 Hours Morning Birds Song | Stress Relief & Focus",
 "8 Hours Forest Birds Sounds | Study, Work, Sleep",
 "8 Hours Beautiful Birds Chirping | Relaxing Nature",
 "8 Hours Peaceful Birds Sounds | Calm Your Mind",
 "8 Hours Birds Sounds in Nature | Sleep & Meditation",
 "8 Hours Soothing Birds Chirping | Deep Focus",
 "8 Hours Forest Morning Birds | Relaxing Ambience",
]
today = datetime.date.today()
day_num = today.timetuple().tm_yday
title = TITLES[day_num % len(TITLES)]
desc = f"""{title}

Enjoy 8 hours of relaxing mixed birds sounds from a peaceful forest.
Different birds chirping together with soft forest ambience.

Perfect for sleep, study, work, meditation and focus.

Subscribe for daily relaxing nature sounds.

#birdssounds #relaxing #nature #sleep #focus #birdschirping"""

# --- 2. PIC - GitHub khud roz nayi layega ---
pic_url = f"https://picsum.photos/seed/birds{day_num}/1280/720"
r = requests.get(pic_url, timeout=30)
open("bg.jpg","wb").write(r.content)
img = Image.open("bg.jpg").convert("RGB")
img.save("bg.jpg")

# --- 3. AWAZAIN MIXED - 3 tarah ki awazain ---
def make_audio():
    sr = 44100
    dur = 15*60
    t = np.linspace(0, dur, int(sr*dur))
    y = np.zeros_like(t)

    # A. Choti chidiya - tez chirp
    for _ in range(90):
        start = random.uniform(0, dur-2)
        f0 = random.uniform(3000, 5200)
        idx = (t>=start)&(t<start+1.5)
        tt = t[idx]-start
        y[idx] += np.sin(2*np.pi*(f0*tt + 400*np.sin(2*np.pi*8*tt))) * np.exp(-tt*2) * 0.35

    # B. Bari chidiya - dheemi coo
    for _ in range(45):
        start = random.uniform(0, dur-3)
        f0 = random.uniform(700, 1400)
        idx = (t>=start)&(t<start+2.5)
        tt = t[idx]-start
        y[idx] += np.sin(2*np.pi*f0*tt) * np.exp(-tt*1) * 0.45

    # C. Door wali chidiya - halki
    for _ in range(60):
        start = random.uniform(0, dur-2)
        f0 = random.uniform(1800, 2800)
        idx = (t>=start)&(t<start+1)
        tt = t[idx]-start
        y[idx] += np.sin(2*np.pi*f0*tt) * np.exp(-tt*2.5) * 0.20

    # D. Hawa / jungle background
    y += np.random.randn(len(t)) * 0.015
    y += np.sin(2*np.pi*180*t) * 0.015

    y = y / (np.max(np.abs(y))+1e-6) * 0.7
    return y, sr

audio_data, sr = make_audio()
def frame(tt):
    i = int(tt*sr)
    return [audio_data[min(i, len(audio_data)-1)]]
audio = AudioClip(frame, duration=15*60, fps=sr)

# --- 4. VIDEO - 15 min ko jor kar 8 ghanta ---
clip = ImageClip("bg.jpg", duration=15*60).with_audio(audio)
clip.write_videofile("part.mp4", fps=24, codec="libx264", audio_codec="aac")
full = concatenate_videoclips([clip]*32)
full.write_videofile("final_8h.mp4", fps=24, codec="libx264", audio_codec="aac")

# --- 5. UPLOAD - Birds Sounds Focus ---
creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
yt = build("youtube","v3", credentials=creds)
req = yt.videos().insert(part={"snippet":{"title":title,"description":desc,"tags":["birds sounds","relaxing","nature"],"categoryId":"10"},"status":{"privacyStatus":"public"}}, media_body=MediaFileUpload("final_8h.mp4", chunksize=-1, resumable=True))
print(req.execute())
print("DONE:", title)
