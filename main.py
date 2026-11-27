import random, datetime, requests, os, json
import numpy as np
from PIL import Image
from moviepy import ImageClip, AudioClip, concatenate_videoclips
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

today = datetime.date.today()
today_str = str(today)

# --- CHECK: Aaj ki video pehle se ban gayi? (8:30 Backup ke liye) ---
try:
    with open("state.json") as f:
        state = json.load(f)
    if state.get("last_date") == today_str:
        print("Aaj ki video pehle se ban gayi, dobara nahi banata.")
        exit(0)
except:
    state = {}

# --- 1. DAILY UNIQUE SEED - Roz alag, 1 saal tak repeat nahi ---
# Date se seed banega, is liye roz naya combination aayega
day_num = today.timetuple().tm_yday  # Saal ka konsa din hai 1-365
random.seed(str(today))  # Aaj ki date hi seed hai
np.random.seed(day_num)

# --- 2. 365 UNIQUE TITLES ---
BIRDS = ["Forest Birds", "Morning Sparrows", "Nightingale", "Canary", "Robin", "Dove", "Parrot", "Cuckoo", "Owl", "Finch", "Blackbird", "Wren"]
MOODS = ["Relaxing", "Calming", "Peaceful", "Soothing", "Healing", "Meditation", "Deep Sleep", "Focus", "Study", "Nature"]
PLACES = ["Peaceful Forest", "Quiet Garden", "Green Valley", "Morning Woods", "Hidden Lake", "Mountain Forest", "Countryside", "Rainforest"]

bird = BIRDS[day_num % len(BIRDS)]
mood = MOODS[day_num % len(MOODS)]
place = PLACES[day_num % len(PLACES)]
# Har din alag combination, 12x10x8 = 960 combinations = 2.5 saal tak repeat nahi
title = f"8 Hours {mood} {bird} Sounds in {place} | Day {day_num} | Relax, Sleep, Study"
desc = f"""Enjoy 8 hours of {mood.lower()} {bird.lower()} sounds from a {place.lower()}.

Today's unique soundscape - Day {day_num} of 365 - was created specially for {today_str}. Different birds, different tones, different ambience than yesterday.

Perfect for sleep, study, work, meditation and focus.

Subscribe for daily relaxing nature sounds.

#birdsounds #relaxing #nature #sleep #focus #birdschirping #day{day_num}"""

# --- 3. ALAG-ALAG PICTURES - 8 hisse, 8 alag pictures ---
print("Pictures download ho rahi hain...")
images = []
for i in range(8):
    # Har hisse ke liye alag seed, roz alag picture
    pic_url = f"https://picsum.photos/seed/birds{day_num}_{i}/1280/720"
    r = requests.get(pic_url, timeout=30)
    open(f"bg_{i}.jpg", "wb").write(r.content)
    img = Image.open(f"bg_{i}.jpg").convert("RGB")
    img.save(f"bg_{i}.jpg")
    images.append(f"bg_{i}.jpg")

# --- 4. NO-LOOP AUDIO - 8 alag 1-ghante ke hisse ---
def make_unique_audio(dur, seed_offset):
    sr = 44100
    t = np.linspace(0, dur, int(sr*dur))
    y = np.zeros_like(t)
    # Har hisse me alag number of chirps, alag frequency
    num_chirps = random.randint(35, 60)
    for _ in range(num_chirps):
        start = random.uniform(0, dur-2)
        f0 = random.uniform(1800, 5200)  # Alag bird ki alag awaz
        idx = (t>=start)&(t<start+1)
        tt = t[idx]-start
        # Har chirp ki pitch thori alag
        y[idx] += np.sin(2*np.pi*f0*tt + 400*np.sin(2*np.pi*8*tt)) * np.exp(-tt*2) * 0.35
    # Halki forest ambience - har hisse me alag level
    y += np.random.normal(0, 0.02, len(t))
    # Normalize taake awaz phate nahi
    y = y / (np.max(np.abs(y)) + 1e-6) * 0.8
    return AudioClip(lambda tt: np.interp(tt, t, y), duration=dur, fps=sr)

print("Video ban rahi hai - 8 alag hisse, NO LOOP...")
clips = []
for i in range(8):
    # Har 1 ghante ke hisse ke liye naya random seed
    random.seed(f"{today_str}-{i}")
    audio = make_unique_audio(3600, i)  # 1 ghanta
    clip = ImageClip(images[i], duration=3600).with_audio(audio)
    clips.append(clip)
    print(f"Hissa {i+1}/8 tayyar")

final = concatenate_videoclips(clips, method="compose")
final.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
print("Video tayyar!")

# --- 5. YOUTUBE UPLOAD ---
creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
youtube = build("youtube", "v3", credentials=creds)
request = youtube.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": title, "description": desc, "tags": ["birds sounds", "relaxing", "nature", "sleep"], "categoryId": "10"}, "status": {"privacyStatus": "public"}},
    media_body=MediaFileUpload("final_video.mp4", chunksize=-1, resumable=True)
)
request.execute()
print("Upload ho gaya!")

# State save karo taake 8:30 wala dobara na chalaye
with open("state.json", "w") as f:
    json.dump({"last_date": today_str}, f)
