# Know Your Background Bot

**Know Your Background** is a small background script written in Python that periodically fetches a short, interesting fact from an OpenAI model and displays a pop-up window saying "Did you know that…". It operates "silently" (through `pythonw.exe`), automatically disappears after a specified timeout, and logs all facts and errors in a file named **`fact_bot.log`** located next to the script. 

## Features

- Random topics from a large pool (~150 fields of knowledge) — facts do not repeat and do not "get stuck" in one era. 
- Nonce token in each request — reduces the likelihood of text duplication. 
- The window always appears above all other applications and closes itself (timeout is configurable). 
- Random interval between requests (default 30–120 mins) — does not seem intrusive and saves tokens. 
- Supports GPT-4o mini (or any other model) with a billing of < $1/month under "default" settings. 
- Maintains a log of all facts and errors.

## Requirements

- **Windows 10/11**
  
- **Python 3.8+** (recommended from Anaconda, but the standard version will also work)

- Libraries:  
    `pip install --upgrade openai tkinter`  
    (tkinter is included in the standard CPython library; it is also pre-installed in Anaconda)
    
- Environment variable **`OPENAI_API_KEY`** with your OpenAI key

## Installation

1. **Download** `know_you_background.py` to a convenient folder, for example:  
    `C:\Scripts\know_you_background.py`
    
2. Make sure the path to `pythonw.exe` is known in your environment, for example:  
    `C:\Users\<you>\anaconda3\pythonw.exe`

## Configuration

At the beginning of the file, you will find the main constants:

```python
MODEL_NAME = "gpt-4o-mini"  # can be "o3" when access is available
TEMPERATURE = 0.9
MIN_DELAY_MIN = 30  # min interval between facts
MAX_DELAY_MIN = 120  # max interval
TIMEOUT_MS = 10_000  # window lives for 10 seconds
# ─── NEW: select level ───
#   "school"   - high school / popular level
#   "undergrad" - senior undergraduate courses
#   "grad"      - master's student / postgraduate
#   "expert"    - advanced (including specialized terms)
LEVEL = "undergrad"
```

*Increase the intervals if you want to call the API less often, or decrease them if you need facts more frequently.*

## Running in the Background (without Console)

### Through a Shortcut

1. Create a **shortcut** with the following target:
    
    ```plaintext
    "C:\Users\<you>\anaconda3\pythonw.exe" "C:\Scripts\know_you_background.py"
    ```
    
2. Place the shortcut in the startup folder:  
    `Win + R` → `shell:startup` → paste the shortcut.

### Through Task Scheduler

- **Task Scheduler → Create Task**
    
    - **Trigger**: *At log on*
        
    - **Action**:  
        *Program*: `pythonw.exe`  
        *Arguments*: `"C:\Scripts\know_you_background.py"`
        
- You can add a delay for startup, conditions like "run only on a network," etc.

### Build .exe (Optional)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole know_you_background.py
```

The resulting `dist\know_you_background.exe` runs the same way, and the shortcut just needs to point to the exe.

## Logs

- All facts and errors are written to `fact_bot.log` (in the same directory as the script). 
- Log line format:

```yaml
2025-07-14 10:15:03,421 INFO FACT: Did you know that...
```

Errors are marked with the level **ERROR** and contain the stack trace.

## Stopping / Removing

- **Once**: `Ctrl + Shift + Esc` → "Details" tab → find `pythonw.exe` with the required path → *End Task*. 
- **Permanently**: remove the shortcut from `shell:startup` or disable/delete the task in Task Scheduler. 
- You can set up a flag file (`stop_facts.txt`) in the code to allow the script to terminate properly by itself.

## Token Savings

With the default settings (a fact approximately every 60 minutes on average), it costs < $1 per month. Increase `MIN_DELAY_MIN` / `MAX_DELAY_MIN` or cache recent facts to reduce expenses even further.

