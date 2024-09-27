import os
import subprocess
import sys
import shutil

def create_directory(dir_name):
    """Klasörün var olup olmadığını kontrol eder, yoksa oluşturur."""
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
            print(f"Klasör oluşturuldu: {dir_name}")
        except Exception as e:
            print(f"{dir_name} klasörü oluşturulamadı: {e}")
            sys.exit(1)
    else:
        print(f"Klasör zaten mevcut: {dir_name}")

def get_user_input(prompt, default=None, validate=None):
    """
    Kullanıcıdan giriş alır, boş bırakılırsa varsayılan değeri kullanır.
    Opsiyonel olarak bir doğrulama fonksiyonu alabilir.
    """
    while True:
        if default:
            user_input = input(f"{prompt} [Varsayılan: {default}]: ").strip()
        else:
            user_input = input(f"{prompt}: ").strip()
        if not user_input and default is not None:
            user_input = default
        if validate:
            valid, message = validate(user_input)
            if valid:
                return user_input
            else:
                print(f"Hata: {message}")
        else:
            return user_input

def check_ffmpeg():
    """FFmpeg'in sistemde yüklü olup olmadığını kontrol eder."""
    if shutil.which("ffmpeg") is None:
        print("Hata: FFmpeg sisteminizde yüklü değil veya PATH'e eklenmemiş.")
        sys.exit(1)
    else:
        print("FFmpeg bulundu.")

def extract_frames(video_path):
    """FFmpeg kullanarak videodan kareleri çıkarır."""
    output_pattern = os.path.join("tmp_frames", "frame%08d.png")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-qscale:v", "1",
        "-qmin", "1",
        "-qmax", "1",
        "-vsync", "0",
        output_pattern
    ]
    print(f"Kareler çıkarılıyor: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("Kareler başarıyla çıkarıldı.")
    except subprocess.CalledProcessError as e:
        print(f"Kare çıkarma işlemi başarısız oldu: {e}")
        sys.exit(1)

def run_realesrgan(realesrgan_path):
    """Realesrgan kullanarak kareleri iyileştirir."""
    input_dir = "tmp_frames"
    output_dir = "out_frames"
    cmd = [
        realesrgan_path,
        "-i", input_dir,
        "-o", output_dir,
        "-n", "realesr-animevideov3",
        "-s", "2",
        "-f", "jpg"
    ]
    print(f"Realesrgan çalıştırılıyor: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("Realesrgan işlemi başarıyla tamamlandı.")
    except subprocess.CalledProcessError as e:
        print(f"Realesrgan işlemi başarısız oldu: {e}")
        sys.exit(1)

def get_video_fps(video_path):
    """FFmpeg kullanarak videonun fps değerini elde eder."""
    cmd = ["ffmpeg", "-i", video_path]
    try:
        # FFmpeg çıktısını stderr'den al
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        stderr = result.stderr

        # Video stream satırını bul
        for line in stderr.split('\n'):
            if "Stream #" in line and "Video:" in line:
                # Örneğin: Stream #0:0: Video: h264 (High), yuv420p(progressive), 1920x1080, 23.98 fps, ...
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if "fps" in part:
                        fps_str = part.split(' ')[0]
                        try:
                            fps = float(fps_str)
                            print(f"Video FPS değeri: {fps}")
                            return fps
                        except ValueError:
                            continue
        print("FPS değeri bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"FPS elde edilirken hata oluştu: {e}")
        sys.exit(1)

def assemble_video_with_audio(fps, video_path, output_name):
    """Ses ekleyerek videoyu birleştirir."""
    cmd = [
        "ffmpeg",
        "-r", str(fps),
        "-i", os.path.join("out_frames", "frame%08d.jpg"),
        "-i", video_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:a", "copy",
        "-c:v", "libx265",
        "-r", str(fps),
        "-pix_fmt", "yuv420p10le",
        output_name
    ]
    print(f"Ses eklenerek video birleştiriliyor: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Video başarıyla oluşturuldu: {output_name}")
    except subprocess.CalledProcessError as e:
        print(f"Video oluşturma işlemi başarısız oldu: {e}")
        sys.exit(1)

def assemble_video_without_audio(fps, output_name):
    """Ses eklemeden videoyu birleştirir."""
    cmd = [
        "ffmpeg",
        "-r", str(fps),
        "-i", os.path.join("out_frames", "frame%08d.jpg"),
        "-c:v", "libx264",
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        output_name
    ]
    print(f"Video ses olmadan birleştiriliyor: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Video başarıyla oluşturuldu: {output_name}")
    except subprocess.CalledProcessError as e:
        print(f"Video oluşturma işlemi başarısız oldu: {e}")
        sys.exit(1)

def validate_video_filename(filename):
    """Dosya adının geçerli bir video uzantısına sahip olup olmadığını kontrol eder."""
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    _, ext = os.path.splitext(filename)
    if ext.lower() in valid_extensions:
        return True, ""
    else:
        return False, f"Lütfen geçerli bir video uzantısı kullanın ({', '.join(valid_extensions)})."

def main():
    # 1. FFmpeg'in varlığını kontrol et
    check_ffmpeg()

    # 2. Klasörleri kontrol et ve oluştur
    create_directory("tmp_frames")
    create_directory("out_frames")

    # 3. Kullanıcıdan video yolu al
    video_path = get_user_input("İşlemek istediğiniz video yolunu girin", default="onepiece_demo.mp4")
    if not os.path.isfile(video_path):
        print(f"Video dosyası bulunamadı: {video_path}")
        sys.exit(1)
    else:
        print(f"Seçilen video yolu: {video_path}")

    # 4. Kareleri çıkar
    extract_frames(video_path)

    # 5. Realesrgan yolunu al
    realesrgan_path = get_user_input("Realesrgan yolunu girin", default="realesrgan-ncnn-vulkan")
    # Check if realesrgan_path is executable
    if shutil.which(realesrgan_path) is None:
        if os.path.isfile(realesrgan_path):
            # Eğer belirtilen yol bir dosya ise
            if not os.access(realesrgan_path, os.X_OK):
                print(f"Realesrgan çalıştırılabilir değil: {realesrgan_path}")
                sys.exit(1)
        else:
            print(f"Realesrgan bulunamadı: {realesrgan_path}")
            sys.exit(1)
    print(f"Realesrgan yolu: {realesrgan_path}")

    # 6. Realesrgan çalıştır
    run_realesrgan(realesrgan_path)

    # 7. Video fps'sini al
    fps = get_video_fps(video_path)

    # 8. Kullanıcıya ses eklemek isteyip istemediğini sor
    while True:
        add_audio = input("Ses eklemek istiyor musunuz? (evet/hayır): ").strip().lower()
        if add_audio in ['evet', 'hayır']:
            break
        else:
            print("Lütfen 'evet' veya 'hayır' olarak cevaplayın.")

    # 9. Çıktı videosunun adını al (geçerli bir video uzantısı ile)
    output_name = get_user_input(
        "Çıktı videosunun adını girin",
        default="output.mp4",
        validate=validate_video_filename
    )

    if add_audio == 'evet':
        # 10. Ses ekleyerek videoyu oluştur
        assemble_video_with_audio(fps, video_path, output_name)
    else:
        # 11. Ses eklemeden videoyu oluştur
        assemble_video_without_audio(fps, output_name)

    print("İşlem tamamlandı.")

if __name__ == "__main__":
    main()
