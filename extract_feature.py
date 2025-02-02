import os
import glob
import subprocess

# Đường dẫn tới thư mục openSMILE mà bạn đã build (chứa SMILExtract.exe và config/)
OPENSMILE_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject\opensmile"

# Đây là đường dẫn đến file thực thi SMILExtract.exe trên Windows
# Điều chỉnh tùy theo nơi bạn build. Ví dụ:
#   C:\Users\Admin\PycharmProjects\PythonProject\opensmile\build\Release\SMILExtract.exe
SMILEXTRACT_EXE = r"C:\Users\Admin\PycharmProjects\PythonProject\opensmile\build\progsrc\smilextract\Release\SMILExtract.exe"

# File config eGeMAPS (có thể dùng eGeMAPSv01b.conf)
EGEMAPS_CONFIG = "egemaps/v01a/eGeMAPSv01a.conf"

# Thư mục chứa CREMA-D audio
AUDIO_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject\combined_wav"

# Thư mục để lưu CSV output
OUTPUT_CSV_DIR = r"C:\Users\Admin\PycharmProjects\PythonProject\cremad_egemaps"

def extract_egemaps_opensmile(
    input_wav: str,
    output_csv: str,
    smilextract_path: str = SMILEXTRACT_EXE,
    opensmile_dir: str = OPENSMILE_DIR,
    config_file: str = EGEMAPS_CONFIG
):
    """
    Gọi openSMILE (SMILExtract.exe) để trích xuất eGeMAPS cho 1 file WAV.
    Lưu kết quả vào file CSV.
    """
    # Đảm bảo file thực thi tồn tại
    if not os.path.isfile(smilextract_path):
        raise FileNotFoundError(f"Không tìm thấy SMILExtract.exe tại: {smilextract_path}")

    # Đường dẫn đầy đủ tới file config eGeMAPS
    config_path = os.path.join(opensmile_dir, "config", config_file)
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Không tìm thấy file config: {config_path}")

    # Tạo folder output nếu chưa có
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Chuẩn bị lệnh gọi SMILExtract
    cmd = [
        smilextract_path,
        "-C", config_path,           # Chọn file config eGeMAPS
        "-I", input_wav,            # Input WAV
        "-O", output_csv,           # Output CSV
        "-instname", os.path.splitext(os.path.basename(input_wav))[0],
        "-appendcsv", "0",          # Tạo file CSV mới
        "-timestampcsv", "1",       # Ghi cột thời gian
        "-csvseparator", ";"        # Dùng dấu ; ngăn cột
    ]

    # Thực thi bằng subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Hiện lỗi nếu fail
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

    print(f"[OK] eGeMAPS extracted: {input_wav} -> {output_csv}")

def batch_extract_egemaps(
    wav_dir: str = AUDIO_DIR,
    output_dir: str = OUTPUT_CSV_DIR
):
    """
    Duyệt file *.wav trong wav_dir, trích xuất eGeMAPS, lưu CSV vào output_dir.
    """
    # Tạo folder output nếu chưa có
    os.makedirs(output_dir, exist_ok=True)

    # Tìm danh sách file WAV
    wav_files = glob.glob(os.path.join(wav_dir, "*.wav"))
    if not wav_files:
        print(f"Không tìm thấy file WAV nào trong {wav_dir}")
        return

    for wav_path in wav_files:
        # Tạo tên file CSV output, ví dụ: 1001_DFA_ANG_XX_egemaps.csv
        basename = os.path.splitext(os.path.basename(wav_path))[0]
        out_csv = os.path.join(output_dir, f"{basename}_egemaps.csv")

        extract_egemaps_opensmile(
            input_wav=wav_path,
            output_csv=out_csv,
            smilextract_path=SMILEXTRACT_EXE,
            opensmile_dir=OPENSMILE_DIR,
            config_file=EGEMAPS_CONFIG
        )

if __name__ == "__main__":
    # Gọi hàm batch_extract_egemaps để trích xuất eGeMAPS cho tất cả .wav trong AUDIO_DIR
    batch_extract_egemaps(
        wav_dir=AUDIO_DIR,
        output_dir=OUTPUT_CSV_DIR
    )
