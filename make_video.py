import os
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# --- LONG VIDEO STYLE SETTING ---
W, H = 1920, 1080
BG_COLOR = (2, 35, 24)  # Deep Green
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT = (255, 235, 170)

ayat_data = [
    ("1", "Alhamdu lillahi Rabbil Aalameen", "Tamam tareefain Allah hi ke liye hain jo tamam jahanon ka paalne wala hai."),
    ("2", "Ar Rahmanir Raheem", "Bara Meherban, Nihayat Reham wala hai."),
    ("3", "Maliki Yaumid Deen", "Badle ke din ka Malik hai."),
    ("4", "Iyyaka Na'budu Wa Iyyaka Nasta'een", "Hum teri hi ibadat karte hain aur tujh hi se madad maangte hain."),
    ("5", "Ihdinas Siratal Mustaqeem", "Humein seedha rasta dikha."),
    ("6", "Siratal Lazeena An'amta Alaihim", "Un logon ka rasta jin par tune inaam kiya."),
    ("7", "Ghairil Maghdoobi Alaihim Walad Dalleen", "Na un ka jin par ghazab hua, aur na gumrahon ka."),
]

os.makedirs("frames", exist_ok=True)
os.makedirs("audio", exist_ok=True)

def get_font(size, bold=True):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    except:
        return ImageFont.load_default()

font_title = get_font(90, True)
font_arabic = get_font(75, True)
font_urdu = get_font(52, False)
font_small = get_font(40, False)

def wrap_text(text, max_len=38):
    words = text.split()
    lines, line = [], ""
    for w in words:
        if len(line + " " + w) < max_len:
            line += " " + w
        else:
            lines.append(line.strip()); line = w
    lines.append(line.strip())
    return lines

# 1. INTRO FRAME - 30 sec ke liye
for idx in range(3):
    img = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw.rectangle([80, 80, W-80, H-80], outline=GOLD, width=6)
    draw.text((W//2, 350), "SURAH AL-FATIHA", font=font_title, fill=GOLD, anchor="mm")
    draw.text((W//2, 500), "Tarjuma Ke Sath", font=font_arabic, fill=WHITE, anchor="mm")
    draw.text((W//2, 620), "Rozana 10 Minute Quran", font=font_small, fill=LIGHT, anchor="mm")
    draw.text((W//2, 900), "Bismillah Hir Rahman Nir Raheem", font=font_small, fill=GOLD, anchor="mm")
    img.save(f"frames/frame_00{idx+1}_intro.png")
tts = gTTS(text="Bismillah Hir Rahman Nir Raheem. Surah Al Fatiha Tarjuma Ke Sath. Aao Quran seekhte hain.", lang='ur')
tts.save("audio/audio_00_intro.mp3")

# 2. HAR AYAT - LONG STYLE
for i, (num, arabic, urdu) in enumerate(ayat_data):
    img = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Top Bar
    draw.rectangle([0, 0, W, 120], fill=(0, 60, 40))
    draw.text((100, 60), f"SURAH FATIHA", font=font_small, fill=GOLD, anchor="lm")
    draw.text((W-100, 60), f"Ayat {num} / 7", font=font_small, fill=WHITE, anchor="rm")
    # Main Arabic
    draw.text((W//2, 380), arabic, font=font_arabic, fill=WHITE, anchor="mm")
    # Line
    draw.line([(400, 500), (W-400, 500)], fill=GOLD, width=3)
    # Urdu Tarjuma
    lines = wrap_text(urdu)
    y = 600
    for l in lines:
        draw.text((W//2, y), l, font=font_urdu, fill=LIGHT, anchor="mm")
        y += 75
    # Progress Bar - Neeche
    progress = int((int(num) / 7) * W)
    draw.rectangle([0, H-30, W, H], fill=(30,30,30))
    draw.rectangle([0, H-30, progress, H], fill=GOLD)
    # Bottom
    draw.text((W//2, H-90), "SUBSCRIBE | LIKE | SHARE", font=font_small, fill=GOLD, anchor="mm")
    img.save(f"frames/frame_{i+1:02d}.png")
    # Audio - 2 baar bolega taake 10 min ho jaye, slow
    text = f"Ayat {num}. {arabic}. Tarjuma: {urdu}. {urdu}."
    tts = gTTS(text=text, lang='ur', slow=True)
    tts.save(f"audio/audio_{i+1:02d}.mp3")
    print(f"Ayat {num} Long Style Done")

# 3. OUTRO FRAME
img = Image.new('RGB', (W, H), color=BG_COLOR)
draw = ImageDraw.Draw(img)
draw.text((W//2, 400), "JAZAKALLAH KHAIR", font=font_title, fill=GOLD, anchor="mm")
draw.text((W//2, 550), "Kal Phir Milenge - Agli Surah Ke Sath", font=font_urdu, fill=WHITE, anchor="mm")
draw.text((W//2, 700), "SUBSCRIBE KARNA MAT BHOOLEN", font=font_small, fill=LIGHT, anchor="mm")
img.save("frames/frame_99_outro.png")
tts = gTTS(text="JazakAllah Khair. Video ko like aur channel ko subscribe zaroor karein. Allah Hafiz.", lang='ur')
tts.save("audio/audio_99_outro.mp3")

print("LONG VIDEO STYLE READY!")
