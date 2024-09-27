import os
import subprocess
from glob import glob

def extract_frames(video_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    command = [
        'ffmpeg',
        '-i', video_path,
        os.path.join(output_folder, 'frame_%04d.png')
    ]
    
    try:
        subprocess.run(command, check=True)
        print("Kareler başarıyla çıkarıldı!")
    except subprocess.CalledProcessError as e:
        print(f"Bir hata oluştu: {e}")

def extract_audio(video_path, audio_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-q:a', '0',
        '-map', 'a',
        audio_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print("Ses başarıyla çıkarıldı!")
    except subprocess.CalledProcessError as e:
        print(f"Ses çıkarılırken bir hata oluştu: {e}")

def upscale_frames(input_folder, output_folder, esrgan_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    input_images = sorted(glob(os.path.join(input_folder, 'frame_*.png')))
    
    if not input_images:
        print("Upscale edilecek kare bulunamadı.")
        return
    
    for img_path in input_images:
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_folder, filename)
        
        command = [
            esrgan_path,
            '-i', img_path,
            '-o', output_path,
            '-n', 'realesrgan-x4plus-anime'
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Upscale edildi: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"{filename} işlenirken bir hata oluştu: {e}")

def create_video_from_frames(input_folder, output_video_path, fps=23.976):
    input_pattern = os.path.join(input_folder, 'frame_%04d.png')
    command = [
        'ffmpeg',
        '-r', str(fps),
        '-i', input_pattern,
        '-c:v', 'libx265',
        '-pix_fmt', 'yuv420p10le',
        output_video_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Video başarıyla oluşturuldu: {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Bir hata oluştu: {e}")

def merge_audio_video(video_path, audio_path, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Ses ve video başarıyla birleştirildi: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ses ve video birleştirilirken bir hata oluştu: {e}")

# Video dosya yolu ve klasör ayarları
video_file = 'input.mp4'
frames_dir = 'frames'
upscaled_frames_dir = 'upscaled_frames'
intermediate_video = 'intermediate.mp4'
output_video = 'output_with_audio.mp4'
esrgan_exe_path = 'realesrgan-ncnn-vulkan.exe'  # realesrgan binary dosyasının yolu
audio_file = 'audio.aac'  # Çıkarılan ses dosyası

# Adım 1: Kareleri videodan çıkar
extract_frames(video_file, frames_dir)

# Adım 2: Ses dosyasını çıkar
extract_audio(video_file, audio_file)

# Adım 3: Kareleri ESRGAN ile upscale et
upscale_frames(frames_dir, upscaled_frames_dir, esrgan_exe_path)

# Adım 4: Upscale edilmiş karelerden yeni bir video oluştur
create_video_from_frames(upscaled_frames_dir, intermediate_video)

# Adım 5: Upscale edilmiş video ile sesi birleştir
merge_audio_video(intermediate_video, audio_file, output_video)

# Opsiyonel: Ara dosyaları temizlemek
# os.remove(intermediate_video)
# os.remove(audio_file)
