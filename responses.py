import re
import random
from memory import update_mood, save_memory
from wiki_handler import get_wiki_summary, last_disambig_options
from math_eval import safe_eval

greetings = ["Hello!", "Hi there!", "Hey!", "Howdy!", "Greetings!"]
farewells = ["Goodbye!", "See you soon!", "Take care!", "Bye for now!"]
thanks_replies = ["You're welcome!", "No problem!", "Glad to help!", "Anytime!"]
fallbacks = [
    "Hmm... I'm still learning. Could you rephrase that?",
    "I'm not sure how to respond, but I'm here to chat!",
    "Interesting! Can you tell me more?",
    "Sorry, I didn't catch that. Want to try again?"
]

rude_words = {"stupid", "idiot", "dumb", "hate", "shut up", "fool"}
nice_words = {"thank", "please", "sorry", "love", "awesome", "great", "good"}

def mood_based_reply(memory, base_reply):
    mood = memory.get("mood", 0)
    if mood >= 3:
        return base_reply + " You're really nice to chat with."
    elif mood <= -3:
        return base_reply + " Hmm, okay smart guy... don't be rude!"
    else:
        return base_reply

def chatbot_response(message, memory):
    global last_disambig_options
    update_mood(memory, message, rude_words, nice_words)
    msg = message.lower().strip()

    if last_disambig_options:
        if msg.isdigit():
            choice = int(msg) - 1
            if 0 <= choice < len(last_disambig_options):
                selected_topic = last_disambig_options[choice]
                last_disambig_options.clear()
                summary = get_wiki_summary(selected_topic)
                return mood_based_reply(memory, summary)
            else:
                return "Please enter a valid option number from the list."
        else:
            for option in last_disambig_options:
                if msg == option.lower():
                    last_disambig_options.clear()
                    summary = get_wiki_summary(option)
                    return mood_based_reply(memory, summary)
            return "Please reply with the number or exact name corresponding to your choice."

    if re.search(r"\b(hi+|hello+|hey+)\b", msg):
        base = random.choice(greetings)
        return mood_based_reply(memory, base)

    elif re.search(r"\b(bye|goodbye|see you)\b", msg):
        base = random.choice(farewells)
        return mood_based_reply(memory, base)

    elif re.search(r"\b(how are you|how's it going)\b", msg):
        return mood_based_reply(memory, "I'm doing great! Thanks for asking. How about you?")

    elif re.search(r"\b(nothing much|just chilling|relaxing)\b", msg):
        return mood_based_reply(memory, "That sounds peaceful.")

    elif msg == "help":
        return ("I can greet you, say goodbye, remember your name, recall your name, "
                "solve math problems, and look things up on Wikipedia.")

    elif re.search(r"\b(thanks|thank you)\b", msg):
        base = random.choice(thanks_replies)
        return mood_based_reply(memory, base)

    elif "my name is" in msg:
        name = " ".join(word.capitalize() for word in msg.split("my name is")[-1].strip().split())
        memory["name"] = name
        save_memory(memory)
        return mood_based_reply(memory, f"Nice to meet you, {name}!")

    elif "what's my name" in msg or "who am i" in msg:
        return mood_based_reply(memory, f"You're {memory.get('name', 'someone mysterious')}!")

    elif re.fullmatch(r"[0-9+\-*/().\s]+", msg):
        try:
            result = safe_eval(msg)
            return mood_based_reply(memory, f"The answer is {result}")
        except Exception:
            return mood_based_reply(memory, "Sorry, I couldn't calculate that.")

    elif msg.startswith("wikipedia ") or msg.startswith("search wikipedia for "):
        query = msg.replace("wikipedia ", "").replace("search wikipedia for ", "").strip()
        return mood_based_reply(memory, get_wiki_summary(query))

    elif msg.startswith("tell me about "):
        query = msg.replace("tell me about ", "").strip()
        return mood_based_reply(memory, get_wiki_summary(query))

    elif msg == "w":
        return mood_based_reply(memory, "absolute cinema")

    else:
        reply = random.choice(fallbacks)
        if reply == "I'm not sure how to respond, but I'm here to chat!":
            wiki_result = get_wiki_summary(message)
            base = f"{reply}\n\nI looked it up for you:\n{wiki_result}"
            return mood_based_reply(memory, base)
        return mood_based_reply(memory, reply)
