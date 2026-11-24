import random, os
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip

birds = [
    ("Parrot", "Parrots can live for more than 80 years and can copy human words."),
    ("Eagle", "Eagles can see a rabbit from 3 kilometers away."),
    ("Owl", "Owls can turn their heads 270 degrees."),
    ("Penguin", "Penguins cannot fly but they are amazing swimmers."),
    ("Peacock", "Peacocks spread their beautiful feathers to attract mates."),
]

name, fact = random.choice(birds)

# 1. Tasveer Banana
img = Image.new('RGB', (1080, 1920), color=(20, 120, 80))
d = ImageDraw.Draw(img)
try:
    f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
    f2 = ImageFont.truetype("DejaVuSans.ttf", 55)
except:
    f1 = ImageFont.load_default()
    f2 = f1
d.text((80, 700), name, fill=(255,255,255), font=f1)
d.text((80, 850), fact, fill=(255,255,0), font=f2)
img.save("bird.jpg")

# 2. Awaz Banana
tts = gTTS(f"{name}. {fact}", lang='en')
tts.save("voice.mp3")

# 3. Video Banana
audio = AudioFileClip("voice.mp3")
clip = ImageClip("bird.jpg").with_duration(audio.duration + 1).with_audio(audio)
clip.write_videofile("bird_video.mp4", fps=24)
print("Video Ban Gayi:", name)
