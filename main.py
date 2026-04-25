import os
import requests
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from dotenv import load_dotenv

# Load API Key dari file .env
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# --- KONFIGURASI NICHE ---
NICHE_PROMPT = "Fakta Unik Psikologi Manusia"

async def generate_voiceover(text, output_file):
    """Mengubah teks menjadi suara (Bahasa Indonesia)"""
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

def get_pexels_video(query):
    """Mencari video vertikal dari Pexels"""
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    r = requests.get(url, headers=headers).json()
    video_url = r['videos'][0]['video_files'][0]['link']
    
    with open("temp_video.mp4", "wb") as f:
        f.write(requests.get(video_url).content)
    return "temp_video.mp4"

def create_video(naskah, video_file, audio_file, output_name):
    """Proses Editing: Menggabungkan Video + Audio + Teks"""
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    
    # Samakan durasi video dengan audio
    video = video.set_duration(audio.duration)
    video = video.set_audio(audio)
    
    # Tambahkan Teks di Tengah (Subtitle)
    txt = TextClip(naskah, fontsize=50, color='white', font='Arial-Bold', 
                   method='caption', size=(video.w*0.8, None))
    txt = txt.set_pos('center').set_duration(video.duration)
    
    final = CompositeVideoClip([video, txt])
    final.write_videofile(f"output/{output_name}.mp4", fps=24, codec="libx264")

async def main():
    # 1. Simulasi Naskah dari AI (Bisa diintegrasikan dengan Gemini API)
    # Contoh naskah pendek 15-30 detik
    naskah = "Tahukah kamu? Secara psikologis, orang yang tertawa berlebihan bahkan untuk hal remeh sebenarnya sedang merasa kesepian."
    keyword_visual = "sad person" # Didapat dari hasil AI
    
    print("Sedang memproses audio...")
    await generate_voiceover(naskah, "temp_audio.mp3")
    
    print("Mencari video di Pexels...")
    video_path = get_pexels_video(keyword_visual)
    
    print("Proses Editing Video...")
    if not os.path.exists("output"): os.makedirs("output")
    create_video(naskah, video_path, "temp_audio.mp3", "video_konten_01")
    
    print("Selesai! Video ada di folder output.")

if __name__ == "__main__":
    asyncio.run(main())
