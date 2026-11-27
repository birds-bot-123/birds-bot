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

# --- 4. SETTING: AUDIO MIX - Bahut saare birds, ek saath ---
print("Asli birds ki awaz download ho rahi hai...")
# Xeno-Canto se asli birds ki awaz - Free, No API Key
SPECIES = ["Passer domesticus", "Luscinia megarhynchos", "Erithacus rubecula", "Streptopelia decaocto", "Psittacula krameri", "Cuculus canorus", "Fringilla coelebs", "Strix aluco", "Serinus canaria", "Turdus merula", "Parus major", "Carduelis carduelis", "Pica pica", "Corvus corone", "Sturnus vulgaris"]

bird_files = []
for i, sp in enumerate(SPECIES):
    try:
        # Xeno-Canto API se us bird ki 1 recording lo
        api = f"https://xeno-canto.org/api/2/recordings?query={sp.replace(' ', '+')}"
        data = requests.get(api, timeout=30).json()
        if data["recordings"]:
            file_url = data["recordings"][0]["file"]
            # file_url //xeno-canto.org/... hota hai, https lagao
            if file_url.startswith("//"):
                file_url = "https:" + file_url
            audio = requests.get(file_url, timeout=60).content
            open(f"bird_{i}.mp3", "wb").write(audio)
            bird_files.append(f"bird_{i}.mp3")
            print(f"Bird {i+1}/15 tayyar: {sp}")
    except Exception as e:
        print(f"Bird {sp} miss ho gaya: {e}")

print(f"Total {len(bird_files)} birds mil gaye, ab MIX ban raha hai...")

# Har ghante ka alag MIX - 8 ghante = 8 alag MIX
hour_files = []
for hour in range(8):
    rng = random.Random(f"{today_str}-hour-{hour}")
    # Har ghante me 5 alag birds chun lo
    chosen = rng.sample(bird_files, min(5, len(bird_files)))
    print(f"Ghanta {hour+1}/8 Mix: {chosen}")
    
    # FFmpeg: 5 birds ko EK SAATH milao, alag-alag volume ke saath
    # Ek tez (0.8), baqi halke (0.4, 0.3, 0.3, 0.2) - jaise jungle me hota hai
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

# 8 ghante ke MIX ko joro - yahan jor nahi pakra jayega kyunki har ghante me alag birds hain + crossfade jaisa feel hai
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
