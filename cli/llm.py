import os
import json
import urllib.request
import urllib.error

def generate_completion(prompt, model="gpt-4o"):
    api_key = os.environ.get("OPENAI_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key and not openrouter_key:
        raise ValueError("Neither OPENAI_API_KEY nor OPENROUTER_API_KEY environment variables are set.")
        
    if openrouter_key:
        # Use OpenRouter configuration
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openrouter_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "ASP Modernization Devkit"
        }
        # If user didn't explicitly override the model, use the requested free model
        if model == "gpt-4o":
            model = "openrouter/free"
            # model = "nvidia/nemotron-3-ultra-550b-a55b:free"
    else:
        # Use standard OpenAI configuration
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert software architect modernizing a Classic ASP application to .NET 10 and React."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    # Enable reasoning for OpenRouter if using their free models
    if openrouter_key:
        data["reasoning"] = {"enabled": True}
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        # Log token usage to ledger
        usage = result.get('usage', {})
        if usage:
            ledger_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'token_ledger.json')
            os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
            ledger_entry = {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "model": model,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
            
            ledger = []
            if os.path.exists(ledger_path):
                try:
                    with open(ledger_path, 'r', encoding='utf-8') as lf:
                        ledger = json.load(lf)
                except:
                    pass
            ledger.append(ledger_entry)
            with open(ledger_path, 'w', encoding='utf-8') as lf:
                json.dump(ledger, lf, indent=2)
                
        return result['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        raise Exception(f"LLM API Error: {e.code} {e.reason} - {error_info}")
    except Exception as e:
        raise Exception(f"Failed to communicate with LLM: {str(e)}")
