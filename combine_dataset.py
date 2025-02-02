import os
import shutil
import glob

########################
# BƯỚC A: Định nghĩa map emotion -> (emo_code, arousal)
########################
# Ta muốn unify emotion code: (ANG, DIS, FEA, HAP, SAD, NEU, SUR, v.v.)
# Arousal: 1 = high, 0 = low
EMOTION_MAP = {
    # TESS & SAVEE & RAVDESS & CREMAD (giả sử):
    # TESS: "angry", "fear", "disgust", "happy", "pleasant_surprise", "sad", "neutral"
    "angry":   ("ANG", 1),
    "fear":    ("FEA", 1),
    "disgust": ("DIS", 1),
    "happy":   ("HAP", 1),
    "sad":     ("SAD", 0),
    "neutral": ("NEU", 0),
    "surprise":("SUR", 1),
    "pleasant_surprise":("SUR", 1),
    # RAVDESS codes
    "calm":    ("NEU", 0),
    # ...
}

def unify_emotion_str(emotion_str: str):
    """
    Trả về (emo_code, arousal_label) từ emotion_str.
    E.g. "angry" -> ("ANG", 1)
         "pleasant_surprise" -> ("SUR",1)
    """
    emotion_str = emotion_str.lower().strip()
    if emotion_str in EMOTION_MAP:
        return EMOTION_MAP[emotion_str]
    # default
    return ("UNK", 0)

########################
# BƯỚC B: Gom TESS
########################
def collect_TESS(tess_root, output_dir):
    """
    TESS folder structure:
      TESS/
        OAF_Fear/   ...
        OAF_angry/  ...
        ...
        YAF_neutral/ ...
      Mỗi file: OAF_back_fear.wav, ...
    """
    # Lấy tất cả subfolder: OAF_Fear, OAF_angry, ...
    subfolders = glob.glob(os.path.join(tess_root, "*_*"))  # e.g. OAF_angry
    for subf in subfolders:
        emotion_raw = os.path.basename(subf).split("_",1)[1]  # "angry", "Fear", ...
        emotion_raw = emotion_raw.lower()
        # unify
        emo_code, aro_label = unify_emotion_str(emotion_raw)

        wav_files = glob.glob(os.path.join(subf, "*.wav"))
        for wfile in wav_files:
            base = os.path.basename(wfile)  # e.g. OAF_back_fear.wav
            # dataset name = "TESS"
            new_name = f"TESS_{emo_code}_{aro_label}.wav"
            # Tuy nhiên, để tránh trùng lặp, ta có thể thêm 1 id = base
            # => TESS_{emo_code}_{aro_label}_{origBase}.wav
            new_name = f"TESS_{emo_code}_{aro_label}_{base}"
            out_path = os.path.join(output_dir, new_name)
            shutil.copy(wfile, out_path)

########################
# BƯỚC C: Gom SAVEE
########################
def collect_SAVEE(savee_root, output_dir):
    """
    SAVEE: /ALL/DC_a02.wav
      speaker = DC/JE/JK/KL
      emotion code = "a" (anger), "d" (disgust), "f"(fear), "h"(happiness), "n"(neutral),
                     "sa"(sadness), "su"(surprise)
    """
    wav_files = glob.glob(os.path.join(savee_root, "*.wav"))
    for wfile in wav_files:
        base = os.path.basename(wfile)  # e.g. DC_a02.wav
        # cắt speaker => DC_, ...
        # Tìm emotion code sau underscore: "a02", "d01", "sa03", ...
        # logic: speaker_emo => "DC_sa03", emo might be "sa03"
        # ta parse 1-2 ký tự, tuỳ "sa" hay "a/d/f/h/n/su"
        # Mẹo: check substring
        name_no_spk = base.split("_",1)[1]  # e.g. "a02.wav" or "sa03.wav"
        # tách 1-2 letters => emotion code
        # handle 2-letter "sa" or "su"
        # handle 1-letter "a,d,f,h,n"
        if name_no_spk.startswith("sa"):
            emotion_raw = "sad"
        elif name_no_spk.startswith("su"):
            emotion_raw = "surprise"
        else:
            code1 = name_no_spk[0]  # 'a','d','f','h','n'
            if code1=="a": emotion_raw="angry"
            elif code1=="d": emotion_raw="disgust"
            elif code1=="f": emotion_raw="fear"
            elif code1=="h": emotion_raw="happy"
            elif code1=="n": emotion_raw="neutral"
            else:
                emotion_raw="unknown"

        emo_code, aro_label = unify_emotion_str(emotion_raw)
        new_name = f"SAVEE_{emo_code}_{aro_label}_{base}"
        out_path = os.path.join(output_dir, new_name)
        shutil.copy(wfile, out_path)

########################
# BƯỚC D: Gom RAVDESS
########################
def collect_RAVDESS(ravdess_root, output_dir):
    """
    RAVDESS: folder Actor_XX, file: "03-01-06-01-02-01-12.wav"
     part[2] = emotion code (01=neutral, 02=calm, 03=happy, 04=sad, 05=angry, 06=fearful, 07=disgust, 08=surprise)
    """
    actor_folders = glob.glob(os.path.join(ravdess_root, "Actor_*"))
    for actf in actor_folders:
        wav_files = glob.glob(os.path.join(actf, "*.wav"))
        for wfile in wav_files:
            base = os.path.basename(wfile)  # "03-01-06-01-02-01-12.wav"
            parts = base.split("-")  # ["03","01","06","01","02","01","12.wav"]
            if len(parts)>=3:
                emo_id = parts[2]  # "06" => fearful
                # map
                if emo_id=="01": emotion_raw="neutral"
                elif emo_id=="02": emotion_raw="calm"  # => neutral
                elif emo_id=="03": emotion_raw="happy"
                elif emo_id=="04": emotion_raw="sad"
                elif emo_id=="05": emotion_raw="angry"
                elif emo_id=="06": emotion_raw="fear"
                elif emo_id=="07": emotion_raw="disgust"
                elif emo_id=="08": emotion_raw="surprise"
                else:
                    emotion_raw="unknown"
            else:
                emotion_raw="unknown"

            emo_code, aro_label = unify_emotion_str(emotion_raw)
            new_name = f"RAVDESS_{emo_code}_{aro_label}_{base}"
            out_path = os.path.join(output_dir, new_name)
            shutil.copy(wfile, out_path)

########################
# BƯỚC E: Gom CREMAD cũ (nếu muốn)
########################
def collect_CREMAD(cremad_dir, output_dir):
    """
    Giả sử Crema-D gốc: /AudioWAV/1001_DFA_ANG_XX.wav => emotion = ANG => unify "ANG"
    Arousal => 1, etc.
    """
    wav_files = glob.glob(os.path.join(cremad_dir, "*.wav"))
    for wfile in wav_files:
        base = os.path.basename(wfile)  # "1001_DFA_ANG_XX.wav"
        parts = base.split("_")
        # parts[2] = e.g. "ANG" => unify
        if len(parts)>=3:
            emo = parts[2].lower()  # "ang"
            # map sang raw string
            if emo=="ang": emotion_raw="angry"
            elif emo=="hap": emotion_raw="happy"
            elif emo=="sad": emotion_raw="sad"
            elif emo=="neu": emotion_raw="neutral"
            elif emo=="fea": emotion_raw="fear"
            elif emo=="dis": emotion_raw="disgust"
            else:
                emotion_raw="unknown"
        else:
            emotion_raw="unknown"

        emo_code, aro_label = unify_emotion_str(emotion_raw)
        new_name = f"CREMAD_{emo_code}_{aro_label}_{base}"
        out_path = os.path.join(output_dir, new_name)
        shutil.copy(wfile, out_path)


########################
# BƯỚC F: HÀM MAIN GỌP TẤT CẢ
########################
def combine_all_datasets(
    tess_root = "C:/Users/Admin/PycharmProjects/PythonProject/TESS Toronto emotional speech set data",
    savee_root= "C:/Users/Admin/PycharmProjects/PythonProject/SAVEE",
    ravdess_root= "C:/Users/Admin/PycharmProjects/PythonProject/RAVDESS",
    cremad_dir = "C:/Users/Admin/PycharmProjects/PythonProject/AudioWAV",
    output_dir = "combined_wav"
):
    os.makedirs(output_dir, exist_ok=True)

    print("Collecting TESS...")
    collect_TESS(tess_root, output_dir)
    print("Collecting SAVEE...")
    collect_SAVEE(savee_root, output_dir)
    print("Collecting RAVDESS...")
    collect_RAVDESS(ravdess_root, output_dir)
    print("Collecting CREMAD...")
    collect_CREMAD(cremad_dir, output_dir)

    print(f"Done! All WAV copied to {output_dir} with unified naming.")


if __name__=="__main__":
    combine_all_datasets()
