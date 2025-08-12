import re
import random
import time
import ast
import wikipedia
import operator as op
import json
import os

# File paths for persistent memory and logs
memory_file = "chat_memory.json"
log_file = "chat_log.txt"

# Load saved memory if it exists
if os.path.exists(memory_file):
    with open(memory_file, "r") as f:
        memory = json.load(f)
else:
    memory = {}

# Predefined response pools
greetings = ["Hello!", "Hi there!", "Hey!", "Howdy!", "Greetings!"]
farewells = ["Goodbye!", "See you soon!", "Take care!", "Bye for now!"]
thanks_replies = ["You're welcome!", "No problem!", "Glad to help!", "Anytime!"]
fallbacks = [
    "Hmm... I'm still learning. Could you rephrase that?",
    "I'm not sure how to respond, but I'm here to chat!",
    "Interesting! Can you tell me more?",
    "Sorry, I didn't catch that. Want to try again?"
]

# Words to detect rude or nice behavior
rude_words = {"stupid", "idiot", "dumb", "hate", "shut up", "fool"}
nice_words = {"thank", "please", "sorry", "love", "awesome", "great", "good"}

# Supported math operators
ops = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg
}

# Global variable to keep track of disambiguation options
last_disambig_options = []

def save_memory():
    with open(memory_file, "w") as f:
        json.dump(memory, f)

def log_conversation(user, bot):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"You: {user}\nBot: {bot}\n")

def get_wiki_summary(query):
    global last_disambig_options
    try:
        summary = wikipedia.summary(query, sentences=2)
        last_disambig_options = []
        return summary
    except wikipedia.DisambiguationError as e:
        last_disambig_options = e.options[:5]
        options_list = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(last_disambig_options))
        return (f"That topic is ambiguous. Please pick one of the options by typing the number or the name:\n{options_list}")
    except wikipedia.PageError:
        last_disambig_options = []
        return "I couldn't find anything about that on Wikipedia."
    except Exception:
        last_disambig_options = []
        return "Sorry, I had trouble accessing Wikipedia."

def safe_eval(expr):
    """Safely evaluate a basic math expression."""
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        else:
            raise TypeError("Unsupported expression")
    return _eval(ast.parse(expr, mode='eval').body)

def update_mood(message):
    msg = message.lower()
    mood_change = 0
    for rude in rude_words:
        if rude in msg:
            mood_change -= 1
    for nice in nice_words:
        if nice in msg:
            mood_change += 1
    memory["mood"] = memory.get("mood", 0) + mood_change
    memory["mood"] = max(-5, min(5, memory["mood"]))  # clamp between -5 and 5
    save_memory()

def mood_based_reply(base_reply):
    mood = memory.get("mood", 0)
    if mood >= 3:
        return base_reply + " \nYou're really nice to chat with."
    elif mood <= -3:
        return base_reply + " \nHmm, okay smart guy... don't be rude!"
    else:
        return base_reply

def chatbot_response(message):
    global last_disambig_options
    update_mood(message)
    msg = message.lower().strip()

    # Handle disambiguation reply: user picks option by number or keyword
    if last_disambig_options:
        # Check if user replied with a number
        if msg.isdigit():
            choice = int(msg) - 1
            if 0 <= choice < len(last_disambig_options):
                selected_topic = last_disambig_options[choice]
                last_disambig_options = []
                summary = get_wiki_summary(selected_topic)
                return mood_based_reply(summary)
            else:
                return "Please enter a valid option number from the list."
        else:
            # Check if user replied with a keyword matching one of the options (case insensitive)
            for option in last_disambig_options:
                if msg == option.lower():
                    last_disambig_options = []
                    summary = get_wiki_summary(option)
                    return mood_based_reply(summary)
            return "Please reply with the number or exact name corresponding to your choice."

    # Greetings
    if re.search(r"\b(hi+|hello+|hey+)\b", msg):
        base = random.choice(greetings)
        return mood_based_reply(base)

    # Farewells
    elif re.search(r"\b(bye|goodbye|see you)\b", msg):
        base = random.choice(farewells)
        return mood_based_reply(base)

    # How are you
    elif re.search(r"\b(how are you|how's it going)\b", msg):
        return mood_based_reply("I'm doing great! Thanks for asking. How about you?")

    # Relaxing replies
    elif re.search(r"\b(nothing much|just chilling|relaxing)\b", msg):
        return mood_based_reply("That sounds peaceful.")

    # Help command
    elif msg == "help":
        return ("I can greet you, say goodbye, remember your name, recall your name, "
                "solve math problems, and look things up on Wikipedia.")

    # Thanks replies
    elif re.search(r"\b(thanks|thank you)\b", msg):
        base = random.choice(thanks_replies)
        return mood_based_reply(base)

    # Remember name
    elif "my name is" in msg:
        name = " ".join(word.capitalize() for word in msg.split("my name is")[-1].strip().split())
        memory["name"] = name
        save_memory()
        return mood_based_reply(f"Nice to meet you, {name}!")

    # Recall name
    elif "what's my name" in msg or "who am i" in msg:
        return mood_based_reply(f"You're {memory.get('name', 'someone mysterious')}!")

    # Math calculation
    elif re.fullmatch(r"[0-9+\-*/().\s]+", msg):
        try:
            result = safe_eval(msg)
            return mood_based_reply(f"The answer is {result}")
        except Exception:
            return mood_based_reply("Sorry, I couldn't calculate that.")

    # Wikipedia searches
    elif msg.startswith("wikipedia ") or msg.startswith("search wikipedia for "):
        query = msg.replace("wikipedia ", "").replace("search wikipedia for ", "").strip()
        return mood_based_reply(get_wiki_summary(query))

    elif msg.startswith("tell me about "):
        query = msg.replace("tell me about ", "").strip()
        return mood_based_reply(get_wiki_summary(query))

    # W meme
    elif msg == "w":
        return mood_based_reply("absolute cinema")

    # Fallback
    else:
        reply = random.choice(fallbacks)
        if reply == "I'm not sure how to respond, but I'm here to chat!":
            wiki_result = get_wiki_summary(message)
            base = f"{reply}\n\nI looked it up for you:\n{wiki_result}"
            return mood_based_reply(base)
        return mood_based_reply(reply)

def chat():
    print("ChatBot: Hi! Type 'help' for commands or 'bye'/'exit' to quit.")
    while True:
        user_input = input("You: ")
        msg = user_input.lower().strip()

        update_mood(user_input)

        if msg in ["bye", "exit"]:
            # Boost mood slightly if polite goodbye
            if any(word in msg for word in nice_words):
                memory["mood"] = min(memory.get("mood", 0) + 1, 5)
            save_memory()
            bot_reply = mood_based_reply(random.choice(farewells))
            log_conversation(user_input, bot_reply)
            print("ChatBot:", bot_reply)
            break

        elif re.search(r"\b(thanks|thank you)\b", msg):
            memory["mood"] = min(memory.get("mood", 0) + 2, 5)  # bigger boost for thanks
            save_memory()
            bot_reply = mood_based_reply(random.choice(thanks_replies))
            log_conversation(user_input, bot_reply)
            print("ChatBot:", bot_reply)
            continue

        time.sleep(0.4)
        response = chatbot_response(user_input)
        log_conversation(user_input, response)
        print("ChatBot:", response)

if __name__ == "__main__":
    chat()

