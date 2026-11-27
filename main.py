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

# --- 4. SETTING: AUDIO MIX - FIXED WALA ---
print("Asli birds ki awaz download ho rahi hai...")
SPECIES = ["Passer domesticus", "Luscinia megarhynchos", "Erithacus rubecula", "Streptopelia decaocto", "Psittacula krameri", "Cuculus canorus", "Fringilla coelebs", "Strix aluco", "Serinus canaria", "Turdus merula", "Parus major", "Carduelis carduelis", "Pica pica", "Corvus corone", "Sturnus vulgaris"]

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 BirdsBot/1.0"}

def get_recording_for(query):
    # v2 pehle, phir v3 - jo bhi chale
    for ver in [2, 3]:
        try:
            api = f"https://xeno-canto.org/api/{ver}/recordings?query={query.replace(' ', '+')}"
            resp = requests.get(api, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                continue
            data = resp.json()
            recs = data.get("recordings", [])
            if recs:
                return recs
        except Exception as e:
            print(f"API v{ver} fail for {query}: {e}")
            continue
    return []

bird_files = []
for i, sp in enumerate(SPECIES):
    try:
        recs = []
        # Try 1: Poora naam - sp:Passer domesticus
        recs = get_recording_for(f"sp:{sp}")
        # Try 2: Sirf pehla naam
        if not recs:
            recs = get_recording_for(sp.split()[0])
        # Try 3: Poora naam bina sp:
        if not recs:
            recs = get_recording_for(sp)

        if recs:
            # Pehli 3 me se koi ek jisme file ho, wo lo - pehli wali kharab bhi ho sakti hai
            got = False
            for rec in recs[:3]:
                file_url = rec.get("file") or rec.get("file-name") or ""
                if not file_url:
                    continue
                if file_url.startswith("//"):
                    file_url = "https:" + file_url
                audio = requests.get(file_url, headers=HEADERS, timeout=60).content
                # Khali file ko skip karo - 5KB se choti file kharab hai
                if len(audio) < 5000:
                    continue
                open(f"bird_{i}.mp3", "wb").write(audio)
                bird_files.append(f"bird_{i}.mp3")
                print(f"Bird {i+1}/15 tayyar: {sp} - {len(audio)} bytes")
                got = True
                break
            if not got:
                print(f"Bird {sp} skip - file kharab thi")
        else:
            print(f"Bird {sp} skip - recording nahi mili")
    except Exception as e:
        print(f"Bird {sp} miss ho gaya: {e}")

# --- BACKUP: Agar phir bhi kam birds mile to generic birds le aao ---
if len(bird_files) < 5:
    print(f"Sirf {len(bird_files)} birds mile, generic birds la raha hun...")
    try:
        recs = get_recording_for("bird song")
        for k, rec in enumerate(recs[:8]):
            try:
                file_url = rec.get("file") or rec.get("file-name") or ""
                if not file_url:
                    continue
                if file_url.startswith("//"):
                    file_url = "https:" + file_url
                audio = requests.get(file_url, headers=HEADERS, timeout=60).content
                if len(audio) < 5000:
                    continue
                fn = f"bird_backup_{k}.mp3"
                open(fn, "wb").write(audio)
                bird_files.append(fn)
                print(f"Backup Bird {k+1} tayyar")
                if len(bird_files) >= 8:
                    break
            except:
                continue
    except Exception as e:
        print(f"Backup fail: {e}")

print(f"Total {len(bird_files)} birds mil gaye, ab MIX ban raha hai...")

if len(bird_files) == 0:
    print("ERROR: Koi bird nahi mila, Xeno-Canto down hai. Dobara try karo.")
    exit(1)

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
