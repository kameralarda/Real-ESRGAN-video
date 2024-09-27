import os
import subprocess
from glob import glob

def extract_frames(video_path, output_folder):
    # Eğer klasör yoksa, oluştur
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # ffmpeg komutunu çalıştırarak kareleri çıkar
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

def upscale_frames(input_folder, output_folder, esrgan_path):
    # Eğer upscale edilmiş kareler için klasör yoksa, oluştur
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Giriş klasöründeki tüm png dosyalarını al
    input_images = sorted(glob(os.path.join(input_folder, 'frame_*.png')))
    
    if not input_images:
        print("Upscale edilecek kare bulunamadı.")
        return
    
    for img_path in input_images:
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_folder, filename)
        
        command = [
            esrgan_path,  # realesrgan-ncnn-vulkan binary dosyasının yolu
            '-i', img_path,
            '-o', output_path,
            '-n', 'realesrgan-x4plus-anime'  # Kullanmak istediğin ESRGAN modeli
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Upscale edildi: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"{filename} işlenirken bir hata oluştu: {e}")

def create_video_from_frames(input_folder, output_video_path, fps=23.976):
    # Karelerden videoyu oluştur
    input_pattern = os.path.join(input_folder, 'frame_%04d.png')
    command = [
        'ffmpeg',
        '-r', str(fps),  # Orijinal FPS (23.976)
        '-i', input_pattern,
        '-c:v', 'libx265',  # HEVC (H.265) codec kullanımı
        '-pix_fmt', 'yuv420p10le',  # Yaygın cihaz uyumu için standart renk formatı
        output_video_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Video başarıyla oluşturuldu: {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Bir hata oluştu: {e}")

# Video dosya yolu ve klasör ayarları
video_file = 'input.mp4'
frames_dir = 'frames'
upscaled_frames_dir = 'upscaled_frames'
output_video = 'output.mp4'
esrgan_exe_path = 'realesrgan-ncnn-vulkan.exe'  # realesrgan binary dosyasının yolu

# Adım 1: Kareleri videodan çıkar
extract_frames(video_file, frames_dir)

# Adım 2: Kareleri ESRGAN ile upscale et
upscale_frames(frames_dir, upscaled_frames_dir, esrgan_exe_path)

# Adım 3: Upscale edilmiş karelerden yeni bir video oluştur
create_video_from_frames(upscaled_frames_dir, output_video)
