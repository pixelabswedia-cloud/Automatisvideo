import os
import requests
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def generate_voiceover(text, output_file):
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

def get_pexels_video(query):
    """Mencari video vertikal dari Pexels dengan pengecekan error"""
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    # Cek apakah API Key benar (Status 200 artinya OK)
    if response.status_code != 200:
        raise Exception(f"Gagal akses Pexels! Status: {response.status_code}. Cek API Key kamu.")
    
    data = response.json()
    
    # Cek apakah hasil pencarian ada
    if 'videos' not in data or len(data['videos']) == 0:
        print(f"Peringatan: Tidak ada video ditemukan untuk '{query}'. Mencoba keyword cadangan...")
        # Jika keyword gagal, coba cari video umum agar tidak error
        return get_pexels_video("nature") 
    
    video_url = data['videos'][0]['video_files'][0]['link']
    print(f"Berhasil menemukan video: {video_url}")
    
    video_data = requests.get(video_url).content
    with open("temp_video.mp4", "wb") as f:
        f.write(video_data)
        
    return "temp_video.mp4"

def create_video(naskah, video_file, audio_file, output_name):
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    if video.duration < audio.duration:
        video = video.loop(duration=audio.duration)
    else:
        video = video.set_duration(audio.duration)
    
    video = video.set_audio(audio)
    
    txt = TextClip(naskah, fontsize=50, color='yellow', font='Arial-Bold', 
                   method='caption', size=(video.w*0.8, None))
    txt = txt.set_pos('center').set_duration(video.duration)
    
    final = CompositeVideoClip([video, txt])
    output_path = f"{output_name}.mp4"
    final.write_videofile(output_path, fps=24, codec="libx264")
    return output_path

async def send_to_telegram(file_path):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    with open(file_path, 'rb') as v:
        await bot.send_video(chat_id=TELEGRAM_CHAT_ID, video=v, caption="Video Baru Siap!")

async def main():
    naskah = "Tahukah kamu? Secara psikologis, tertawa berlebihan meski untuk hal kecil bisa jadi tanda seseorang merasa kesepian."
    keyword = "lonely person"
    
    await generate_voiceover(naskah, "temp_audio.mp3")
    video_path = get_pexels_video(keyword)
    final_video = create_video(naskah, video_path, "temp_audio.mp3", "konten_harian")
    
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        await send_to_telegram(final_video)

if __name__ == "__main__":
    asyncio.run(main())
