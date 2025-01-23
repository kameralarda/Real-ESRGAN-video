import os
import subprocess
import shutil
import zipfile
import requests
from pathlib import Path

def download_file(url, dest):
    try:
        print(f"{url} indiriliyor...")
        response = requests.get(url, stream=True)
        with open(dest, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"{dest} başarıyla indirildi.")
    except Exception as e:
        print(f"Dosya indirilirken bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def extract_zip(file_path, extract_to):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"{file_path}, {extract_to} klasörüne başarıyla çıkarıldı.")
    except Exception as e:
        print(f"ZIP dosyası çıkarılırken bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def add_to_path(new_path):
    try:
        current_path = os.environ.get("PATH", "")
        if new_path not in current_path:
            subprocess.run(f"setx PATH \"{new_path};%PATH%\"", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{new_path} sistem yollarına başarıyla eklendi.")
    except Exception as e:
        print(f"Sistem yoluna ekleme sırasında bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def check_7zip():
    try:
        subprocess.run(["7z"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("7-Zip zaten yüklü.")
        return True
    except FileNotFoundError:
        print("7-Zip yüklü değil.")
        return False

def install_7zip():
    try:
        url = "https://7-zip.org/a/7z2409-x64.exe"
        installer_path = "C:/7zip_installer.exe"

        download_file(url, installer_path)

        subprocess.run([installer_path, "/S", "/D=C:\\7-Zip"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        add_to_path("C:/7-Zip")
        print("7-Zip başarıyla kuruldu ve sistem yollarına eklendi.")

        os.remove(installer_path)
        print(f"Kurulum dosyası ({installer_path}) silindi.")
    except Exception as e:
        print(f"7-Zip kurulumu sırasında bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def extract_7z(file_path, extract_to):
    try:
        subprocess.run(["7z", "x", file_path, f"-o{extract_to}"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{file_path}, {extract_to} klasörüne başarıyla çıkarıldı.")
    except Exception as e:
        print(f"7z dosyası çıkarılırken bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg zaten yüklü.")
        return True
    except FileNotFoundError:
        print("FFmpeg yüklü değil.")
        return False

def install_ffmpeg():
    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z"
        download_path = "C:/ffmpeg.7z"
        extract_path = "C:/"

        download_file(url, download_path)

        extract_7z(download_path, extract_path)
        os.rename("C:/ffmpeg-7.1-full_build", "C:/ffmpeg")
        add_to_path("C:/ffmpeg/bin")
        print("FFmpeg başarıyla kuruldu ve sistem yollarına eklendi.")

        os.remove(download_path)
        print(f"Kurulum dosyası ({download_path}) silindi.")
    except Exception as e:
        print(f"FFmpeg kurulumu sırasında bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def check_realesrgan():
    try:
        subprocess.run(["realesrgan-ncnn-vulkan"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Real-ESRGAN zaten yüklü.")
        return True
    except FileNotFoundError:
        print("Real-ESRGAN yüklü değil.")
        return False

def install_realesrgan():
    try:
        url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip"
        download_path = "C:/realesrgan.zip"
        extract_path = "C:/realesrgan"

        download_file(url, download_path)

        os.makedirs(extract_path, exist_ok=True)
        extract_zip(download_path, extract_path)
        add_to_path(extract_path)
        print("Real-ESRGAN başarıyla kuruldu ve sistem yollarına eklendi.")

        os.remove(download_path)
        print(f"Kurulum dosyası ({download_path}) silindi.")
    except Exception as e:
        print(f"Real-ESRGAN kurulumu sırasında bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")
        raise

def main():
    try:
        if not check_7zip():
            user_input = input("7-Zip yüklü değil. İndirmek ister misiniz? (e/h): ").lower()
            if user_input == 'e':
                install_7zip()
            else:
                print("Program sonlandırıldı.")
                input("Devam etmek için Enter'a basın...")
                return

        if not check_ffmpeg():
            user_input = input("FFmpeg yüklü değil. İndirmek ister misiniz? (e/h): ").lower()
            if user_input == 'e':
                install_ffmpeg()
            else:
                print("Program sonlandırıldı.")
                input("Devam etmek için Enter'a basın...")
                return

        if not check_realesrgan():
            user_input = input("Real-ESRGAN yüklü değil. İndirmek ister misiniz? (e/h): ").lower()
            if user_input == 'e':
                install_realesrgan()
            else:
                print("Program sonlandırıldı.")
                input("Devam etmek için Enter'a basın...")
                return

        video_path = input("Upscale yapmak istediğiniz videonun yolunu girin: ")
        video_path = Path(video_path)

        if not video_path.exists():
            print("Girilen video dosyası bulunamadı.")
            input("Devam etmek için Enter'a basın...")
            return

        tmp_frames = video_path.parent / "tmp_frames"
        out_frames = video_path.parent / "out_frames"

        tmp_frames.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-i", str(video_path), "-qscale:v", "1", "-qmin", "1", "-qmax", "1", "-vsync", "0", str(tmp_frames / "frame%08d.png")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        out_frames.mkdir(exist_ok=True)
        subprocess.run(["realesrgan-ncnn-vulkan", "-i", str(tmp_frames), "-o", str(out_frames), "-n", "realesr-animevideov3", "-s", "2", "-f", "jpg"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        shutil.rmtree(tmp_frames)

        fps_result = subprocess.run(["ffmpeg", "-i", str(video_path)], stderr=subprocess.PIPE, text=True)
        fps_line = [line for line in fps_result.stderr.splitlines() if "fps" in line and "Video" in line]

        if fps_line:
            fps = fps_line[0].split(",")[4].strip().split(" ")[0]
            print(f"FPS algılandı: {fps}")
        else:
            fps = "23.98"
            print("FPS algılanamadı, varsayılan FPS kullanılıyor: 23.98")

        upscale_video_path = video_path.parent / f"{video_path.stem}_upscaled.mp4"
        subprocess.run(["ffmpeg", "-r", fps, "-i", str(out_frames / "frame%08d.jpg"), "-i", str(video_path), "-map", "0:v:0", "-map", "1:a:0", "-c:a", "copy", "-c:v", "libx264", "-r", fps, "-pix_fmt", "yuv420p", str(upscale_video_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        shutil.rmtree(out_frames)

        print("İşlem tamamlandı. Sonuç dosyaları:")
        print(f"1. Orijinal video: {video_path}")
        print(f"2. Upscale edilmiş video: {upscale_video_path}")
        input("İşlem başarıyla tamamlandı. Devam etmek için Enter'a basın...")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        input("Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
