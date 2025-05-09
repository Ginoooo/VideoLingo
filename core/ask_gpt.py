import os, sys, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from threading import Lock
import json_repair
import json 
from openai import OpenAI
import time
from requests.exceptions import RequestException
from core.config_utils import load_key

LOG_FOLDER = 'output/gpt_log'
LOCK = Lock()

def save_log(model, prompt, response, log_title = 'default', message = None):
    os.makedirs(LOG_FOLDER, exist_ok=True)
    log_data = {
        "model": model,
        "prompt": prompt,
        "response": response,
        "message": message
    }
    log_file = os.path.join(LOG_FOLDER, f"{log_title}.json")
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_data)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
        
def check_ask_gpt_history(prompt, model, log_title):
    if not os.path.exists(LOG_FOLDER):
        return False
    file_path = os.path.join(LOG_FOLDER, f"{log_title}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if item["prompt"] == prompt:
                    return item["response"]
    return False

def fix_base_url(base_url):
    if 'ark' in base_url:
        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        return base_url
    if 'v1' not in base_url:
        base_url = base_url.strip('/') + '/v1'
    return base_url

def ask_gpt(prompt, response_json=True, valid_def=None, log_title='default'):
    api_set = load_key("api")
    llm_support_json = load_key("llm_support_json")

    if isinstance(api_set["key"], list):
        keys = api_set["key"]
        current_key_index = getattr(ask_gpt, "_current_key_index", 0)
        api_key = keys[current_key_index]
        ask_gpt._current_key_index = (current_key_index + 1) % len(keys)
    else:
        api_key = api_set["key"]
    with LOCK:
        history_response = check_ask_gpt_history(prompt, api_set["model"], log_title)
        if history_response:
            return history_response

    if not api_key:
        raise ValueError(f"⚠️API_KEY is missing")
    
    print("api:", api_key)
    messages = [{"role": "user", "content": prompt}]
    
    base_url = fix_base_url(api_set["base_url"])
    client = OpenAI(api_key=api_key, base_url=base_url)
    response_format = {"type": "json_object"} if response_json and api_set["model"] in llm_support_json else None

    max_retries = 3
    for attempt in range(max_retries):
        try:
            completion_args = {
                "model": api_set["model"],
                "messages": messages
            }
            if response_format is not None:
                completion_args["response_format"] = response_format
            print(f"Using API key index: {current_key_index}") if 'current_key_index' in locals() else None
            response = client.chat.completions.create(**completion_args)
            
            if response_json:
                try:
                    response_data = json_repair.loads(response.choices[0].message.content)

                    if valid_def:
                        valid_response = valid_def(response_data)
                        if valid_response['status'] != 'success':
                            save_log(api_set["model"], prompt, response_data, log_title="error", message=valid_response['message'])
                            raise ValueError(f"❎ API response error: {valid_response['message']}")

                    break
                except Exception as e:
                    response_data = response.choices[0].message.content
                    print(f"❎ json_repair parsing failed. Retrying: '''{response_data}'''")
                    save_log(api_set["model"], prompt, response_data, log_title="error", message=f"json_repair parsing failed.")
                    if attempt == max_retries - 1:
                        raise Exception(f"JSON parsing still failed after {max_retries} attempts: {e}\n Please check your network connection or API key or `output/gpt_log/error.json` to debug.")
            else:
                response_data = response.choices[0].message.content
                break

        except Exception as e:
            if attempt < max_retries - 1:
                if isinstance(e, RequestException):
                    print(f"Request error: {e}. Retrying ({attempt + 1}/{max_retries})...")
                else:
                    print(f"Unexpected error occurred: {e}\nRetrying...")
                time.sleep(2)
            else:
                raise Exception(f"Still failed after {max_retries} attempts: {e}")
    with LOCK:
        if log_title != 'None':
            save_log(api_set["model"], prompt, response_data, log_title=log_title)

    return response_data


if __name__ == '__main__':
    print(ask_gpt('hi there hey response in json format, just return 200.' , response_json=True, log_title=None))