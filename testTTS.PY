from pathlib import Path
from rich import print as rprint
import requests

def cosyvoice_tts(text, text_lang, save_path, ref_audio_path, prompt_lang, prompt_text):
    current_dir = Path.cwd()
    
    payload = {
        'text': text,
        # 'role': "中文女",
        # # role: '中文女', '中文男', '日语男', '粤语女', '英文女', '英文男', '韩语女'
        'reference_audio': str('./asset/kunkunpro_全民制作人们大家好，我是练习时长两年半的个人练习生蔡徐坤.wav'),
        'reference_text': prompt_text,
    }

    def save_audio(response, save_path, current_dir):
        if save_path:
            full_save_path = current_dir / save_path
            full_save_path.parent.mkdir(parents=True, exist_ok=True)
            full_save_path.write_bytes(response.content)
            rprint(f"[bold green]Audio saved successfully:[/bold green] {full_save_path}")
        return True
    
    print("Requesting TTS...", payload)

    response = requests.post('http://127.0.0.1:9233/clone_eq', data=payload, timeout=3600)
    if response.status_code == 200:
        return save_audio(response, save_path, current_dir)
    else:
        rprint(f"[bold red]TTS request failed, status code:[/bold red] {response.status_code, response.reason}")
        return False

def gpt_sovits_tts(text, text_lang, save_path, ref_audio_path, prompt_lang, prompt_text):
    current_dir = Path.cwd()
    
    payload = {
        'text': text,
        'text_lang': text_lang,
        # 'ref_audio_path': str(ref_audio_path),
        'ref_audio_path': str('GPT_SoVITS/configs/kunkunpro_全民制作人们大家好，我是练习时长两年半的个人练习生蔡徐坤.wav'),
        'prompt_lang': prompt_lang,
        'prompt_text': prompt_text,
        "speed_factor": 1.0,
    }

    def save_audio(response, save_path, current_dir):
        if save_path:
            full_save_path = current_dir / save_path
            full_save_path.parent.mkdir(parents=True, exist_ok=True)
            full_save_path.write_bytes(response.content)
            rprint(f"[bold green]Audio saved successfully:[/bold green] {full_save_path}")
        return True
    
    print("Requesting TTS...", payload)

    response = requests.post('http://127.0.0.1:9880/tts', json=payload)
    # response = requests.post('http://10.19.233.185:9880/tts', json=payload)
    if response.status_code == 200:
        return save_audio(response, save_path, current_dir)
    else:
        rprint(f"[bold red]TTS request failed, status code:[/bold red] {response.status_code, response.reason}")
        return False
    

def find_and_check_config_path(dubbing_character):
    current_dir = Path(__file__).resolve().parent
    print("current_dir = ", current_dir)
    parent_dir = current_dir.parent
    print("parent_dir = ", parent_dir)
    
    # Find the GPT-SoVITS-v2 directory
    gpt_sovits_dir = next((d for d in parent_dir.iterdir() if d.is_dir() and d.name.startswith('GPT-SoVITS-v2')), None)

    if gpt_sovits_dir is None:
        raise FileNotFoundError("GPT-SoVITS-v2 directory not found in the parent directory.")

    config_path = gpt_sovits_dir / "GPT_SoVITS" / "configs" / f"{dubbing_character}.yaml"   
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    return gpt_sovits_dir, config_path
    

DUBBING_CHARACTER = "kunkunpro"
_, config_path = find_and_check_config_path(DUBBING_CHARACTER)
print("gpt_sovits_dir = ", config_path)
config_dir = config_path.parent

# Find reference audio file
ref_audio_files = list(config_dir.glob(f"{DUBBING_CHARACTER}_*.wav")) + list(config_dir.glob(f"{DUBBING_CHARACTER}_*.mp3"))
if not ref_audio_files:
    raise FileNotFoundError(f"No reference audio file found for {DUBBING_CHARACTER}")
ref_audio_path = ref_audio_files[0]

# Extract content from filename
content = ref_audio_path.stem.split('_', 1)[1]

#! Check. Only support zh and en.
prompt_lang = 'zh'

print(f"Detected language: {prompt_lang}")
prompt_text = content

success = cosyvoice_tts(" AMD急需FSR4打一场漂亮Ai翻身仗", "zh", "temp/1.wav", ref_audio_path, prompt_lang, prompt_text)
# success = gpt_sovits_tts("这 1500 美元差价包含 M<zh>3<zh> Ultra  芯片", "zh", "temp/1.wav", ref_audio_path, prompt_lang, prompt_text)

print("ret = ", success)