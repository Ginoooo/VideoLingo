import pandas as pd
import datetime
import os, sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ask_gpt import ask_gpt
from core.prompts_storage import get_subtitle_trim_prompt
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from core.config_utils import load_key  
from core.all_tts_functions.estimate_duration import init_estimator, estimate_duration

console = Console()
speed_factor = load_key("speed_factor")

TRANS_SUBS_FOR_AUDIO_FILE = 'output/audio/trans_subs_for_audio.srt'
SRC_SUBS_FOR_AUDIO_FILE = 'output/audio/src_subs_for_audio.srt'
SOVITS_TASKS_FILE = 'output/audio/tts_tasks.xlsx'
SUBTITLE_FILES = [TRANS_SUBS_FOR_AUDIO_FILE, SRC_SUBS_FOR_AUDIO_FILE, 'output/trans.srt']  # Files to process
ESTIMATOR = None

# Define replacement dictionary
REPLACEMENTS = {
    'NVIDIA': '<zh>NVIDIA<zh>',
    'CUDA': '<zh>CUDA<zh>',
    'AI': '<zh>AI<zh>',
    'ZEN': '<zh>ZEN<zh>',
    'Intel': '<zh>Intel<zh>',
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
    '5050': '<number>5050<number>',
    '5060': '<number>5060<number>',
    '5070': '<number>5070<number>',
    '5080': '<number>5080<number>',
    '5090': '<number>5090<number>',
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
    '8GB'  : '<number>8<number>GB',
    '12GB'  : '<number>12<number>GB',
    '16GB'  : '<number>16<number>GB',
    '24GB'  : '<number>24<number>GB',
    '32GB'  : '<number>32<number>GB',
    '64GB'  : '<number>64<number>GB',
    '96GB'  : '<number>96<number>GB',
    '128GB'  : '<number>128<number>GB',
    '256GB'  : '<number>256<number>GB',
    '512GB'  : '<number>512<number>GB',
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
    'X3D'  : '<zh>X3D<zh>',
    '3D'  : '<number>3<number>D',
    '2D'  : '<number>2<number>D',
    'X99'  : 'X<number>99<number>',
    'X79'  : 'X<number>79<number>',
    # AMD锐龙型号
    '9950'  : '<number>9950<number>',
    '9900'  : '<number>9900<number>',
    '9800'  : '<number>9800<number>',
    '9700'  : '<number>9700<number>',
    '9600'  : '<number>9600<number>',
    '5600'  : '<number>5600<number>',
    '7700'  : '<number>7700<number>',
    '7800'  : '<number>7800<number>',
    '7900'  : '<number>7900<number>',
    '7950'  : '<number>7950<number>',
    '5800'  : '<number>5800<number>',
    '5900'  : '<number>5900<number>',
    '5800X'  : '<number>5800<number>X',
    '5900X'  : '<number>5900<number>X',
    '5600X'  : '<number>5600<number>X',
    '5700X'  : '<number>5700<number>X',
    '5800X'  : '<number>5800<number>X',
    '5900X'  : '<number>5900<number>X',
    '5950X'  : '<number>5950<number>X',
    # intel型号
    'i9'  : 'i<number>9<number>',
    'i7'  : 'i<number>7<number>',
    'i5'  : 'i<number>5<number>',
    'i3'  : 'i<number>3<number>',
    # 13代 intelcpu
    '13600'  : '<number>13600<number>',
    '13600F'  : '<number>13600<number>F',
    '13600K'  : '<number>13600<number>K',
    '13600KF'  : '<number>13600<number>KF',
    '13700'  : '<number>13700<number>',
    '13700F'  : '<number>13700<number>F',
    '13700K'  : '<number>13700<number>K',
    '13700KF'  : '<number>13700<number>KF',
    '13900'  : '<number>13900<number>',
    '13900F'  : '<number>13900<number>F',
    '13900K'  : '<number>13900<number>K',
    '13900KF'  : '<number>13900<number>KF',
    # 14代 intelcpu
    '14600K'  : '<number>14600<number>K',
    '14700'  : '<number>14700<number>',
    '14700F'  : '<number>14700<number>F',
    '14700K'  : '<number>14700<number>K',
    '14700KF'  : '<number>14700<number>KF',
    '14900'  : '<number>14900<number>',
    '14900F'  : '<number>14900<number>F',
    '14900K'  : '<number>14900<number>K',
    '14900KF'  : '<number>14900<number>KF',
    # 制造工艺(nm)
    'N3B'  : 'N<number>3<number>B',
    'N5P'  : 'N<number>5<number>P',
    'N6'  : 'N<number>6<number>',
    # 酷睿Ultra家族
    '285K'  : '<number>285<number>K',
    '285'  : '<number>285<number>',
    '285T'  : '<number>285<number>T',
    '265K'  : '<number>265<number>K',
    '265KF'  : '<number>265<number>KF',
    '265'  : '<number>265<number>',
    '265F'  : '<number>265<number>F',
    '265T'  : '<number>265<number>T',
    '245K'  : '<number>245<number>K',
    '245KF'  : '<number>245<number>KF',
    '245'  : '<number>245<number>',
    '245T'  : '<number>245<number>T',
    '235'  : '<number>235<number>',
    '235T'  : '<number>235<number>T',
    '235F'  : '<number>235<number>F',
    '225'  : '<number>225<number>',
    '225F'  : '<number>225<number>F',
    '225T'  : '<number>225<number>T',
    '205'  : '<number>205<number>',
    
    'DLSS2': 'DLSS<number>2<number>',
    'DLSS3': 'DLSS<number>3<number>',
    'DLSS3.5': 'DLSS<number>3.5<number>',
    'DLSS4': 'DLSS<number>4<number>',
    'DLSS5': 'DLSS<number>5<number>',
    'DLSS6': 'DLSS<number>6<number>',
    'FSR2': 'FSR<number>2<number>',
    'FSR3': 'FSR<number>3<number>',
    '2.2': '<number>2.2<number>',
    '3.1': '<number>3.1<number>',
    'FSR3.5': 'FSR<number>3.5<number>',
    'FSR4': 'FSR<number>4<number>',
    'FSR5': 'FSR<number>5<number>',
    'FSR6': 'FSR<number>6<number>',
    '9060': '<number>9060<number>',
    '9070': '<number>9070<number>',
    '9080': '<number>9080<number>',
    '9090': '<number>9090<number>',
    'AMD': 'Amd',
    'FSR': 'Fsr',
}

def replace_non_tag_text(text):
    """只在非标签内容部分进行关键词替换"""
    parts = re.split(r'(<[^>]+>)', text)  # 分割标签和普通内容
    for i in range(len(parts)):
        if i % 2 == 0:  # 仅处理非标签部分（偶数索引）
            for key, value in REPLACEMENTS.items():
                parts[i] = re.sub(
                    rf'\b{re.escape(key)}\b', 
                    value, 
                    parts[i], 
                    flags=re.IGNORECASE
                )
    return ''.join(parts)

def replace_in_subtitle_files():
    """Replace words in all specified subtitle files"""
    for subtitle_file in SUBTITLE_FILES:
        if not os.path.exists(subtitle_file):
            continue
            
        with open(subtitle_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Skip if already processed
        if "#REPLACED#" in content:
            rprint(Panel(f"{subtitle_file} already processed, skipping", title="Info", border_style="blue"))
            continue
            
        # Split into blocks and process each one
        blocks = content.strip().split('\n\n')
        processed_blocks = []

        for block in blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if len(lines) < 3:  # Skip malformed blocks
                processed_blocks.append(block)
                continue

            # Keep number and timestamp lines as-is
            number_line = lines[0]
            time_line = lines[1]
            text_lines = lines[2:]

            # Process only the text content
            text_content = ' '.join(text_lines)
            # text_content = replace_non_tag_text(text_content)  # 使用新方法替换
            # for key, value in REPLACEMENTS.items():
            #     pattern = re.compile(r'\b' + re.escape(key) + r'\b', flags=re.IGNORECASE)
            #     text_content = pattern.sub(value, text_content)
                
            # Rebuild the block
            processed_block = f"{number_line}\n{time_line}\n{text_content}"
            processed_blocks.append(processed_block)

        # Add processed marker and join blocks
        content = '\n\n'.join(processed_blocks) + "\n\n#REPLACED#\n"
        with open(subtitle_file, 'w', encoding='utf-8') as file:
            file.write(content)
            
        rprint(Panel(f"Processed replacements in {subtitle_file}", title="Success", border_style="green"))

def check_len_then_trim(text, duration):
    global ESTIMATOR
    if ESTIMATOR is None:
        ESTIMATOR = init_estimator()
    estimated_duration = estimate_duration(text, ESTIMATOR) / speed_factor['max']
    
    console.print(f"Subtitle text: {text}, "
                  f"[bold green]Estimated reading duration: {estimated_duration:.2f} seconds[/bold green]")

    if estimated_duration > duration:
        rprint(Panel(f"Estimated reading duration {estimated_duration:.2f} seconds exceeds given duration {duration:.2f} seconds, shortening...", title="Processing", border_style="yellow"))
        original_text = text
        prompt = get_subtitle_trim_prompt(text, duration)
        def valid_trim(response):
            if 'result' not in response:
                return {'status': 'error', 'message': 'No result in response'}
            return {'status': 'success', 'message': ''}
        try:    
            response = ask_gpt(prompt, response_json=True, log_title='subtitle_trim', valid_def=valid_trim)
            shortened_text = response['result']
        except Exception:
            rprint("[bold red]🚫 AI refused to answer due to sensitivity, so manually remove punctuation[/bold red]")
            shortened_text = re.sub(r'[,.!?;:，。！？；：]', ' ', text).strip()
        rprint(Panel(f"Subtitle before shortening: {original_text}\nSubtitle after shortening: {shortened_text}", title="Subtitle Shortening Result", border_style="green"))
        return shortened_text
    else:
        return text

def time_diff_seconds(t1, t2, base_date):
    """Calculate the difference in seconds between two time objects"""
    dt1 = datetime.datetime.combine(base_date, t1)
    dt2 = datetime.datetime.combine(base_date, t2)
    return (dt2 - dt1).total_seconds()

def process_srt():
    """Process srt file, generate audio tasks"""
    
    with open(TRANS_SUBS_FOR_AUDIO_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    with open(SRC_SUBS_FOR_AUDIO_FILE, 'r', encoding='utf-8') as src_file:
        src_content = src_file.read()
    
    subtitles = []
    src_subtitles = {}
    
    for block in src_content.strip().split('\n\n'):
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        
        number = int(lines[0])
        src_text = ' '.join(lines[2:])
        src_subtitles[number] = src_text
    
    for block in content.strip().split('\n\n'):
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        
        try:
            number = int(lines[0])
            start_time, end_time = lines[1].split(' --> ')
            start_time = datetime.datetime.strptime(start_time, '%H:%M:%S,%f').time()
            end_time = datetime.datetime.strptime(end_time, '%H:%M:%S,%f').time()
            duration = time_diff_seconds(start_time, end_time, datetime.date.today())
            text = ' '.join(lines[2:])
            # Remove content within parentheses (including English and Chinese parentheses)
            text = re.sub(r'\([^)]*\)', '', text).strip()
            text = re.sub(r'（[^）]*）', '', text).strip()
            # Remove '-' character, can continue to add illegal characters that cause errors
            text = text.replace('-', '')

            # Add the original text from src_subs_for_audio.srt
            origin = src_subtitles.get(number, '')

        except ValueError as e:
            rprint(Panel(f"Unable to parse subtitle block '{block}', error: {str(e)}, skipping this subtitle block.", title="Error", border_style="red"))
            continue
        
        subtitles.append({'number': number, 'start_time': start_time, 'end_time': end_time, 'duration': duration, 'text': text, 'origin': origin})
    
    df = pd.DataFrame(subtitles)
    
    i = 0
    MIN_SUB_DUR = load_key("min_subtitle_duration")
    while i < len(df):
        today = datetime.date.today()
        if df.loc[i, 'duration'] < MIN_SUB_DUR:
            if i < len(df) - 1 and time_diff_seconds(df.loc[i, 'start_time'],df.loc[i+1, 'start_time'],today) < MIN_SUB_DUR:
                rprint(f"[bold yellow]Merging subtitles {i+1} and {i+2}[/bold yellow]")
                df.loc[i, 'text'] += ' ' + df.loc[i+1, 'text']
                df.loc[i, 'origin'] += ' ' + df.loc[i+1, 'origin']
                df.loc[i, 'end_time'] = df.loc[i+1, 'end_time']
                df.loc[i, 'duration'] = time_diff_seconds(df.loc[i, 'start_time'],df.loc[i, 'end_time'],today)
                df = df.drop(i+1).reset_index(drop=True)
            else:
                if i < len(df) - 1:  # Not the last audio
                    rprint(f"[bold blue]Extending subtitle {i+1} duration to {MIN_SUB_DUR} seconds[/bold blue]")
                    df.loc[i, 'end_time'] = (datetime.datetime.combine(today, df.loc[i, 'start_time']) + 
                                            datetime.timedelta(seconds=MIN_SUB_DUR)).time()
                    df.loc[i, 'duration'] = MIN_SUB_DUR
                else:
                    rprint(f"[bold red]The last subtitle {i+1} duration is less than {MIN_SUB_DUR} seconds, but not extending[/bold red]")
                i += 1
        else:
            i += 1
    
    df['start_time'] = df['start_time'].apply(lambda x: x.strftime('%H:%M:%S.%f')[:-3])
    df['end_time'] = df['end_time'].apply(lambda x: x.strftime('%H:%M:%S.%f')[:-3])

    return df

def gen_audio_task_main():
    # First process replacements in subtitle files
    replace_in_subtitle_files()
    
    if os.path.exists(SOVITS_TASKS_FILE):
        rprint(Panel(f"{SOVITS_TASKS_FILE} already exists, skip.", title="Info", border_style="blue"))
    else:
        df = process_srt()
        console.print(df)
        df.to_excel(SOVITS_TASKS_FILE, index=False)

        rprint(Panel(f"Successfully generated {SOVITS_TASKS_FILE}", title="Success", border_style="green"))

if __name__ == '__main__':
    gen_audio_task_main()

