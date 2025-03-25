import os
import sys
import re
import pandas as pd
import soundfile as sf
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.all_whisper_methods.demucs_vl import demucs_main, VOCAL_AUDIO_FILE

# Simplified path definitions
REF_DIR = 'output/audio/refers'
SEG_DIR = 'output/audio/segs'
TASKS_FILE = 'output/audio/tts_tasks.xlsx'
SUBTITLE_FILES = ['trans_subs_for_audio.srt', 'trans.srt']  # List your subtitle files here

console = Console()

def time_to_samples(time_str, sr):
    """Unified time conversion function"""
    h, m, s = time_str.split(':')
    s, ms = s.split(',') if ',' in s else (s, '0')
    seconds = int(h) * 3600 + int(m) * 60 + float(s) + float(ms) / 1000
    return int(seconds * sr)

def extract_audio(audio_data, sr, start_time, end_time, out_file):
    """Simplified audio extraction function"""
    start = time_to_samples(start_time, sr)
    end = time_to_samples(end_time, sr)
    sf.write(out_file, audio_data[start:end], sr)

def replace_with_tags(file_name, replacements):
    """Replace specific strings in the subtitle file with tags"""
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Check if the file has already been replaced
    if any("#REPLACED#\n" in line for line in lines):
        rprint(Panel(f"{file_name} 已经被处理过，跳过替换", title="Info", border_style="blue"))
        return False

    # Function to replace content
    def replace_content(match):
        return f"<zh>{match.group(0)}</zh>"

    # Apply all replacements to each line
    for key in replacements:
        pattern = re.compile(r'\b' + re.escape(key) + r'\b', flags=re.IGNORECASE)
        lines = [pattern.sub(replace_content, line) for line in lines]

    # Add the replaced marker to the file
    lines.append("#REPLACED#\n")

    with open(file_name, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    return True

def replace_in_subtitle_files(replacements):
    """Replace words in all specified subtitle files"""
    for subtitle_file in SUBTITLE_FILES:
        if replace_with_tags(subtitle_file, replacements):
            rprint(Panel(f"Replacements made in {subtitle_file}", title="Info", border_style="blue"))

def extract_refer_audio_main():
    demucs_main()  # Run demucs if not already run
    if os.path.exists(os.path.join(SEG_DIR, '1.wav')):
        rprint(Panel("Audio segments already exist, skipping extraction", title="Info", border_style="blue"))
        return

    # Create output directory
    os.makedirs(REF_DIR, exist_ok=True)
    
    # Read task file and audio data
    df = pd.read_excel(TASKS_FILE)
    data, sr = sf.read(VOCAL_AUDIO_FILE)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Extracting audio segments...", total=len(df))
        
        for _, row in df.iterrows():
            out_file = os.path.join(REF_DIR, f"{row['number']}.wav")
            extract_audio(data, sr, row['start_time'], row['end_time'], out_file)
            progress.update(task, advance=1)
            
    rprint(Panel(f"Audio segments saved to {REF_DIR}", title="Success", border_style="green"))

def main():
    # Define replacement dictionary
    replacements = {
        'NVIDIA': '英伟达',
        'CUDA': '酷的',
        'AI': '<zh>AI<zh>',
        'ZEN': '真',
        'Intel': '英特尔',
        'Ryzen': '锐龙',
        'SUPER': 'Super',
        'MAX': 'Max',
        'TI': 'Ti',
        'PRO': 'Pro',
        'PLUS': 'Plus',
        'ULTRA': 'Ultra',
        'TITAN': 'Titan',
        'QUADRO': 'Quadro',
        'CORE': 'Core',
        '1050': '<number>1050<number>',
        '1060': '<number>1060<number>',
        '1070': '<number>1070<number>',
        '1080': '<number>1080<number>',
        '2050': '<number>2050<number>',
        '2060': '<number>2060<number>',
        '2070': '<number>2070<number>',
        '2080': '<number>2080<number>',
        '3050': '<number>3050<number>',
        '3060': '<number>3060<number>',
        '3070': '<number>3070<number>',
        '3080': '<number>3080<number>',
        '3090': '<number>3090<number>',
        '4050': '<number>4050<number>',
        '4060': '<number>4060<number>',
        '4070': '<number>4070<number>',
        '4080': '<number>4080<number>',
        '4090': '<number>4090<number>',
        '1440': '<number>1440<number>',
        '3840': '<number>3840<number>',
        '2160': '<number>2160<number>',
        '2077': '<number>2077<number>',
        'M1'  : 'M<number>1<number>',
        'M2'  : 'M<number>2<number>',
        'M3'  : 'M<number>3<number>',
        'M4'  : 'M<number>4<number>',
        'M5'  : 'M<number>5<number>',
        'M6'  : 'M<number>6<number>',
        'M.1'  : 'M<number>1<number>',
        'M.2'  : 'M<number>2<number>',
        'M.3'  : 'M<number>3<number>',
        'M.4'  : 'M<number>4<number>',
        'M.5'  : 'M<number>5<number>',
        'M.6'  : 'M<number>6<number>',
        '860M'  : '<number>860<number>M',
        '880M'  : '<number>880<number>M',
        '890M'  : '<number>890<number>M',
        '395'  : '<number>395<number>',
        '390'  : '<number>390<number>',
        '385'  : '<number>385<number>',
        '370'  : '<number>370<number>',
        '365'  : '<number>365<number>',
        'Z13'  : 'Z<number>13<number>',
        'Z14'  : 'Z<number>14<number>',
        'X3D'  : '叉<number>3<number>滴',
        # AMD锐龙型号
        '9950'  : '<number>9950<number>',
        '9900'  : '<number>9900<number>',
        '9800'  : '<number>9800<number>',
        '9700'  : '<number>9700<number>',
        '9600'  : '<number>9600<number>',
        '5600'  : '<number>5600<number>',
        # intel型号
        'i9'  : 'i<number>9<number>',
        'i7'  : 'i<number>7<number>',
        'i5'  : 'i<number>5<number>',
        'i3'  : 'i<number>3<number>',
    }

    # Replace words in subtitle files
    replace_in_subtitle_files(replacements)

    # Extract refer audio
    extract_refer_audio_main()

if __name__ == "__main__":
    main()
