from pathlib import Path
import requests
from rich import print as rprint
import os, sys
import subprocess
import socket
import time
import requests
import re
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from core.config_utils import load_key

CosyVoiceServer = "10.19.233.185"

TERM_REPLACEMENTS = {
    # CPU 型号
    "395": "三九五",
    "390": "三九零",
    "385": "三八五",
    "380": "三八零",
    "375": "三七五",
    "370": "三七零",
    "365": "三六五",
    "360": "三六零",
    "355": "三五五",
    "350": "三五零",
    "345": "三四五",
    "340": "三四零",
    
    "285": "二八五",
    "280": "二八零",
    "275": "二七五",
    "270": "二七零",
    "265": "二六五",
    "260": "二六零",
    "255": "二五五",
    "250": "二五零",
    "245": "二四五",
    "240": "二四零",
    "235": "二三五",
    "230": "二三零",
    "225": "二二五",
    "220": "二二零",
    "215": "二一五",
    "210": "二一零",
    "205": "二零五",
    "200": "二零零",
    
    
    "9070": "九零七零",
    "9060": "九零六零",
    "9050": "九零五零",
    
    "8090": "八零九零",
    "8080": "八零八零",
    "8070": "八零七零",
    "8060": "八零六零",
    "8050": "八零五零",
    
    "7090": "七零九零",
    "7080": "七零八零",
    "7070": "七零七零",
    "7060": "七零六零",
    "7050": "七零五零",
    
    "6090": "六零九零",
    "6080": "六零八零",
    "6070": "六零七零",
    "6060": "六零六零",
    "6050": "六零五零",
   
    "5090": "五零九零",
    "5080": "五零八零",
    "5070": "五零七零",
    "5060": "五零六零",
    "5050": "五零五零",
    
    "4090": "四零九零",
    "4080": "四零八零",
    "4070": "四零七零",
    "4060": "四零六零",
    "4050": "四零五零",
    
    "3090": "三零九零",
    "3080": "三零八零",
    "3070": "三零七零",
    "3060": "三零六零",
    "3050": "三零五零",
    
    "2080": "二零八零",
    "2070": "二零七零",
    "2060": "二零六零",
    "2050": "二零五零",
    
    "1080": "一零八零",
    "1070": "一零七零",
    "1060": "一零六零",
    "1050": "一零五零",
    
    
    "2020": "二零二零",
    "2021": "二零二一",
    "2022": "二零二二",
    "2023": "二零二三",
    "2024": "二零二四",
    "2025": "二零二五",
    "2026": "二零二六",
    "2027": "二零二七",
    "2028": "二零二八",
    "2029": "二零二九",
    "2030": "二零三零",
    "2077": "二零七七",

    # Add more mappings here as needed
}

def preprocess_text_for_tts(text):
    """Replace specific terms in the text to improve TTS pronunciation."""
    for term, replacement in TERM_REPLACEMENTS.items():
        text = text.replace(term, replacement)

    text = re.sub(r'(\d+)-(\d+)', r'\1、\2', text)

    return text

def check_lang(text_lang, prompt_lang):
    # only support zh and en
    if any(lang in text_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        text_lang = 'zh'
    elif any(lang in text_lang.lower() for lang in ['英文', '英语', 'english']):
        text_lang = 'en'
    else:
        raise ValueError("Unsupported text language. Only Chinese and English are supported.")
    
    if any(lang in prompt_lang.lower() for lang in ['en', 'english', '英文', '英语']):
        prompt_lang = 'en'
    elif any(lang in prompt_lang.lower() for lang in ['zh', 'cn', '中文', 'chinese']):
        prompt_lang = 'zh'
    else:
        raise ValueError("Unsupported prompt language. Only Chinese and English are supported.")
    return text_lang, prompt_lang


def cosyvoice_tts(text, text_lang, save_path, ref_audio_path, prompt_lang, prompt_text):
    current_dir = Path.cwd()
    
    # Preprocess the input text
    processed_text = preprocess_text_for_tts(text)
    
    payload = {
        'text': processed_text,
        # 'role': "中文女",
        # # role: '中文女', '中文男', '日语男', '粤语女', '英文女', '英文男', '韩语女'
        # 'reference_audio': str('./asset/kunkunpro_全民制作人们大家好，我是练习时长两年半的个人练习生蔡徐坤.wav'),
        # 'reference_text': "全民制作人们大家好，我是练习时长两年半的个人练习生蔡徐坤",
        'reference_audio': str('./asset/maikou_我们会制作一个功能强大的背包系统，他也要负责交易，还有建造.wav'),
        'reference_text': "我们会制作一个功能强大的背包系统，他也要负责交易，还有建造",
    }

    def save_audio(response, save_path, current_dir):
        if save_path:
            full_save_path = current_dir / save_path
            full_save_path.parent.mkdir(parents=True, exist_ok=True)
            full_save_path.write_bytes(response.content)
            rprint(f"[bold green]Audio saved successfully:[/bold green] {full_save_path}")
        return True
    
    print("Requesting TTS...", payload)

    # response = requests.post('http://10.19.233.185:9233/clone_eq', data=payload, timeout=3600)
    response = requests.post('http://127.0.0.1:9233/clone_eq', data=payload, timeout=3600)
    if response.status_code == 200:
        return save_audio(response, save_path, current_dir)
    else:
        rprint(f"[bold red]TTS request failed, status code:[/bold red] {response.status_code, response.reason}")
        return False

def cosy_voice_tts_for_videolingo(text, save_as, number, task_df):
    # start_gpt_sovits_server()
    TARGET_LANGUAGE = load_key("target_language")
    WHISPER_LANGUAGE = load_key("whisper.language")
    sovits_set = load_key("gpt_sovits")
    DUBBING_CHARACTER = sovits_set["character"]
    REFER_MODE = sovits_set["refer_mode"]

    current_dir = Path.cwd()
    prompt_lang = load_key("whisper.detected_language") if WHISPER_LANGUAGE == 'auto' else WHISPER_LANGUAGE
    prompt_text = task_df.loc[task_df['number'] == number, 'origin'].values[0]

    if REFER_MODE == 1:
        # Use the default reference audio from config
        _, config_path = find_and_check_config_path(DUBBING_CHARACTER)
        config_dir = config_path.parent

        # Find reference audio file
        ref_audio_files = list(config_dir.glob(f"{DUBBING_CHARACTER}_*.wav")) + list(config_dir.glob(f"{DUBBING_CHARACTER}_*.mp3"))
        if not ref_audio_files:
            raise FileNotFoundError(f"No reference audio file found for {DUBBING_CHARACTER}")
        ref_audio_path = ref_audio_files[0]

        # Extract content from filename
        content = ref_audio_path.stem.split('_', 1)[1]
        
        #! Check. Only support zh and en.
        prompt_lang = 'zh' if any('\u4e00' <= char <= '\u9fff' for char in content) else 'en'
        
        print(f"Detected language: {prompt_lang}")
        prompt_text = content
    elif REFER_MODE in [2, 3]:
        # Check if the reference audio file exists
        ref_audio_path = current_dir / ("output/audio/refers/1.wav" if REFER_MODE == 2 else f"output/audio/refers/{number}.wav")
        if not ref_audio_path.exists():
            # If the file does not exist, try to extract the reference audio
            try:
                from core.step9_extract_refer_audio import extract_refer_audio_main
                rprint(f"[yellow]Reference audio file does not exist, attempting extraction: {ref_audio_path}[/yellow]")
                extract_refer_audio_main()
            except Exception as e:
                rprint(f"[bold red]Failed to extract reference audio: {str(e)}[/bold red]")
                raise
    else:
        raise ValueError("Invalid REFER_MODE. Choose 1, 2, or 3.")

    success = cosyvoice_tts(text, TARGET_LANGUAGE, save_as, ref_audio_path, prompt_lang, prompt_text)
    if not success and REFER_MODE == 3:
        rprint(f"[bold red]TTS request failed, switching back to mode 2 and retrying[/bold red]")
        ref_audio_path = current_dir / "output/audio/refers/1.wav"
        cosyvoice_tts(text, TARGET_LANGUAGE, save_as, ref_audio_path, prompt_lang, prompt_text)


def find_and_check_config_path(dubbing_character):
    current_dir = Path(__file__).resolve().parent.parent.parent
    parent_dir = current_dir.parent

    # Find the GPT-SoVITS-v2 directory
    gpt_sovits_dir = next((d for d in parent_dir.iterdir() if d.is_dir() and d.name.startswith('GPT-SoVITS-v')), None)

    if gpt_sovits_dir is None:
        raise FileNotFoundError("GPT-SoVITS-v2 directory not found in the parent directory.")

    config_path = gpt_sovits_dir / "GPT_SoVITS" / "configs" / f"{dubbing_character}.yaml"   
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    return gpt_sovits_dir, config_path

def start_gpt_sovits_server():
    current_dir = Path(__file__).resolve().parent.parent.parent
    # Check if port 9880 is already in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 9880))
    if result == 0:
        sock.close()
        return None
    sock.close()

    rprint("[bold yellow]🚀 Initializing GPT-SoVITS Server...[/bold yellow]")
    rprint("[bold yellow]🚀 正在初始化 GPT-SoVITS 服务器...[/bold yellow]")
    
    rprint("""[bold red]⏳ Please wait approximately 1 minute
  • A new command prompt will appear for the GPT-SoVITS API
  • Any `404 not found` warnings during startup are normal, please be patient[/bold red]""")
    rprint("""[bold red]⏳ 请等待大约1分钟
  • GPT-SoVITS API 将会打开一个新的命令提示符窗口
  • 启动过程中出现 `404 not found` 警告是正常的，请耐心等待[/bold red]""")
    
    # Find and check config path
    gpt_sovits_dir, config_path = find_and_check_config_path(load_key("gpt_sovits.character"))

    # Change to the GPT-SoVITS-v2 directory
    os.chdir(gpt_sovits_dir)

    if sys.platform == "win32":
        cmd = [
            "runtime\\python.exe",
            "api_v2.py",
            "-a", "127.0.0.1",
            "-p", "9880",
            "-c", str(config_path)
        ]
        # Open the command in a new window on Windows
        process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    elif sys.platform == "darwin":  # macOS
        print("Please manually start the GPT-SoVITS server at http://127.0.0.1:9880, refer to api_v2.py.")
        while True:
            user_input = input("Have you started the server? (y/n): ").lower()
            if user_input == 'y':
                process = None
                break
            elif user_input == 'n':
                raise Exception("Please start the server before continuing.")
    else:
        raise OSError("Unsupported operating system. Only Windows and macOS are supported.")

    # Change back to the original directory
    os.chdir(current_dir)

    # Wait for the server to start (max 30 seconds)
    start_time = time.time()
    while time.time() - start_time < 50:
        try:
            time.sleep(15)
            response = requests.get('http://127.0.0.1:9880/ping')
            if response.status_code == 200:
                print("GPT-SoVITS server is ready.")
                return process
        except requests.exceptions.RequestException:
            pass

    raise Exception("GPT-SoVITS server failed to start within 50 seconds. Please check if GPT-SoVITS-v2-xxx folder is set correctly.")
