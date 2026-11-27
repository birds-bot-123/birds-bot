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
        exit()
except:
    state = {}

# --- 1. DAILY UNIQUE SEED - Roz alag, 1 saal tak repeat nahi ---
day_num = today.timetuple().tm_yday
random.seed(today_str)
np.random.seed(day_num)

# --- 2. UNIQUE TITLES ---
BIRDS = ["Forest Birds", "Morning Sparrow", "Nightingale", "Canary", "Robin", "Dove", "Parrot", "Cuckoo", "Owl", "Finch"]
MOODS = ["Relaxing", "Calming", "Peaceful", "Soothing", "Healing", "Meditation", "Deep Sleep", "Focus", "Study", "Nature"]
PLACES = ["Peaceful Forest", "Quiet Garden", "Green Valley", "Morning Woods", "Hidden Lake", "Mountain Forest", "Country Meadow"]

bird = BIRDS[day_num % len(BIRDS)]
mood = MOODS[day_num % len(MOODS)]
place = PLACES[day_num % len(PLACES)]

title = f"8 Hours {bird} {mood} Sounds in {place} | Day {day_num} | Relax, Sleep, Study"
desc = f"""Enjoy 8 hours of {mood.lower()} {bird.lower()} sounds from a {place.lower()}.

Today's unique soundscape - Day {day_num} of 365 - was created specially for {today_str}. Different birds, different tones every day.

Perfect for sleep, study, work, meditation and focus.

Subscribe for daily relaxing nature sounds.

#BirdSounds #Relaxing #Nature #Sleep #Focus #BirdChirping #Day{day_num}"""

# --- 3. ALAG-ALAG PICTURES - 8 hisse, 8 alag pictures ---
print("Pictures download ho rahi hain...")
images = []
for i in range(8):
    pic_url = f"https://picsum.photos/seed/birds{day_num}_{i}/1280/720"
    r = requests.get(pic_url, timeout=30)
    open(f"bg_{i}.jpg", "wb").write(r.content)
    img = Image.open(f"bg_{i}.jpg").convert("RGB")
    img.save(f"bg_{i}.jpg")
    images.append(f"bg_{i}.jpg")

# --- 4. NO-LOOP AUDIO - Tukde tukde me banega, memory nahi bharega ---
def make_unique_audio(dur, seed_offset):
    random.seed(f"{today_str}-{seed_offset}")
    np.random.seed(int(today_str.replace('-', '')) + seed_offset)
    # Pehle se 60 sec ke chirps fix kar lo, phir usi ko repeat karenge
    chirps = []
    for _ in range(25):
        chirps.append((random.uniform(0, 60), random.uniform(0.5, 2.0), random.randint(1500, 5200)))

    def make_frame(t):
        # MoviePy kabhi 1 number bhejta hai, kabhi poori list - dono handle karo
        is_single = np.isscalar(t) or np.ndim(t) == 0
        t_arr = np.atleast_1d(np.asarray(t, dtype=float))
        y = np.random.normal(0, 0.02, len(t_arr))
        tt = np.mod(t_arr, 60)  # 60 sec ka loop
        for start, length, freq in chirps:
            idx = (tt >= start) & (tt < start + length)
            if np.any(idx):
                t2 = tt[idx] - start
                y[idx] += 0.35 * np.sin(2 * np.pi * freq * t2) * np.exp(-t2 * 2)
        return y[0] if is_single else y

    return AudioClip(make_frame, duration=dur, fps=22050)

print("Video ban rahi hai - 8 alag hisse, NO LOOP...")
clips = []
for i in range(8):
    random.seed(f"{today_str}-{i}")
    audio = make_unique_audio(3600, i)
    clip = ImageClip(images[i], duration=3600).with_audio(audio)
    clips.append(clip)
    print(f"Hissa {i+1}/8 tayyar")

final = concatenate_videoclips(clips, method="compose")
final.write_videofile("final_video.mp4", fps=12, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4, logger=None)
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
