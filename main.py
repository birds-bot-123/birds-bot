
import random, datetime, requests, os, json, subprocess

today = datetime.date.today()
today_str = str(today)
day_num = today.timetuple().tm_yday

# --- 1. SETTING: Dobara na bane (5:30 backup ke liye) ---
try:
    with open("state.json") as f:
        state = json.load(f)
    if state.get("last_date") == today_str:
        print("Aaj ki video pehle se ban gayi, dobara nahi banata.")
        exit()
except:
    state = {}

# --- 2. SETTING: Title / Description - Har din naya ---
BIRDS = ["Forest Birds", "Morning Sparrow", "Nightingale", "Canary", "Robin", "Dove", "Parrot", "Cuckoo", "Owl", "Finch"]
MOODS = ["Relaxing", "Calming", "Peaceful", "Soothing", "Healing", "Meditation", "Deep Sleep", "Focus", "Study", "Nature"]
PLACES = ["Peaceful Forest", "Quiet Garden", "Green Valley", "Morning Woods", "Hidden Lake", "Mountain Forest", "Country Meadow"]

bird = BIRDS[(day_num * 3 + 1) % len(BIRDS)]
mood = MOODS[(day_num * 7 + 2) % len(MOODS)]
place = PLACES[(day_num * 5 + 3) % len(PLACES)]

title = f"8 Hours {bird} {mood} Sounds in {place} | Day {day_num} | Relax, Sleep, Study"
desc = f"""Enjoy 8 hours of {mood.lower()} {bird.lower()} sounds from a {place.lower()}.

Today's unique soundscape - Day {day_num} of 365 - was created specially for {today_str}. Different birds, different tones every day.

Perfect for sleep, study, work, meditation and focus.

Subscribe for daily relaxing nature sounds.

#BirdSounds #Relaxing #Nature #Sleep #Focus #BirdChirping #Day{day_num}"""

# --- 3. SETTING: Photo - Sirf 1, har din nayi ---
print("Photo download ho rahi hai...")
pic_url = f"https://picsum.photos/seed/birds{day_num}_{today_str}/1280/720"
r = requests.get(pic_url, timeout=30)
open("bg.jpg", "wb").write(r.content)
print("Photo tayyar!")

# --- 4. SETTING: AUDIO MIX - GITHUB KHUD BANAYEGA, KUCH DOWNLOAD NAHI ---
print("GitHub khud birds ki awaz bana raha hai...")

import wave, math, random

def make_chirp_file(filename, seed):
    random.seed(seed)
    sr = 44100
    duration = 30
    audio = [0.0] * (sr * duration)
    t_start = 0
    while t_start < duration:
        f0 = random.uniform(2000, 4000)
        f1 = random.uniform(3500, 6000)
        chirp_len = random.uniform(0.2, 0.5)
        vol = random.uniform(0.5, 0.9)
        for i in range(int(chirp_len * sr)):
            tt = i / sr
            freq = f0 + (f1 - f0) * math.sin(3.14 * tt / chirp_len * 2)
            val = math.sin(2 * 3.14159 * freq * tt) * vol
            val = val * math.sin(3.14159 * tt / chirp_len)
            pos = int((t_start + tt) * sr)
            if pos < len(audio):
                audio[pos] += val
        t_start += random.uniform(1.5, 3.0)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for v in audio:
            v = max(-1.0, min(1.0, v * 0.8))
            wf.writeframes(int(v * 32767).to_bytes(2, 'little', signed=True))
    return filename

bird_files = []
for i in range(15):
    wav = f"bird_{i}.wav"
    seed = int(today_str.replace("-", "")) + i * 100
    make_chirp_file(wav, seed)
    subprocess.run(["ffmpeg", "-y", "-i", wav, f"bird_{i}.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bird_files.append(f"bird_{i}.mp3")
    print(f"Bird {i+1}/15 tayyar: GitHub ne khud banayi!")

print(f"Total {len(bird_files)} birds mil gaye, ab MIX ban raha hai...")

# Har ghante ka alag MIX - 8 ghante = 8 alag MIX
hour_files = []
for hour in range(8):
    rng = random.Random(f"{today_str}-hour-{hour}")
    # Har ghante me 5 alag birds chun lo
    chosen = rng.sample(bird_files, min(5, len(bird_files)))
    print(f"Ghanta {hour+1}/8 Mix: {chosen}")
    
    volumes = [0.8, 0.4, 0.35, 0.3, 0.25]
    inputs = []
    filters = []
    for j, bf in enumerate(chosen):
        inputs.extend(["-stream_loop", "-1", "-i", bf])
        filters.append(f"[{j}:a]volume={volumes[j]}[a{j}]")
    
    filter_complex = ";".join(filters) + f";{''.join([f'[a{j}]' for j in range(len(chosen))])}amix=inputs={len(chosen)}:duration=longest:dropout_transition=0[aout]"
    
    cmd_mix = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[aout]", "-t", "3600", "-c:a", "aac", "-b:a", "128k", f"hour_{hour}.m4a"]
    subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    hour_files.append(f"hour_{hour}.m4a")

with open("concat.txt", "w") as f:
    for hf in hour_files:
        f.write(f"file '{hf}'\n")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "full_8h.m4a"], check=True)
print("8 ghante ka MIX tayyar!")

# --- 5. SETTING: Video - FFmpeg, 1 Photo + 8 Ghante Audio ---
print("Video ban rahi hai...")
cmd_video = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", "bg.jpg",
    "-i", "full_8h.m4a",
    "-t", "28800",
    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
    "-c:a", "copy", "-shortest",
    "final_video.mp4"
]
subprocess.run(cmd_video, check=True)
print("Video tayyar!")

# --- 6. SETTING: YouTube Upload ---
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/youtube.upload"])
youtube = build("youtube", "v3", credentials=creds)
request = youtube.videos().insert(
    part="snippet,status",
    body={"snippet": {"title": title, "description": desc, "tags": ["birds sounds", "relaxing", "nature", "sleep"], "categoryId": "10"}, "status": {"privacyStatus": "public"}},
    media_body=MediaFileUpload("final_video.mp4", chunksize=-1, resumable=True)
)
request.execute()
print("Upload ho gaya!")

with open("state.json", "w") as f:
    json.dump({"last_date": today_str}, f)
