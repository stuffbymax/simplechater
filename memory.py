import json
import os

memory_file = "chat_memory.json"

def load_memory():
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)
    else:
        return {}

def save_memory(memory):
    with open(memory_file, "w") as f:
        json.dump(memory, f)

def update_mood(memory, message, rude_words, nice_words):
    msg = message.lower()
    mood_change = 0
    for rude in rude_words:
        if rude in msg:
            mood_change -= 1
    for nice in nice_words:
        if nice in msg:
            mood_change += 1
    memory["mood"] = memory.get("mood", 0) + mood_change
    memory["mood"] = max(-5, min(5, memory["mood"]))  # clamp
    save_memory(memory)
