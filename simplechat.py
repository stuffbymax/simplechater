import re
import random
import time

# Memory for user-specific info
memory = {}

# Predefined response pools
greetings = ["Hello!", "Hi there!", "Hey!", "Howdy!", "Greetings! 😊"]
farewells = ["Goodbye!", "See you soon!", "Take care!", "Bye for now! 👋"]
thanks_replies = ["You're welcome!", "No problem!", "Glad to help!", "Anytime! 😊"]
fallbacks = [
    "Hmm... I'm still learning. Could you rephrase that?",
    "I'm not sure how to respond, but I'm here to chat!",
    "Interesting! Can you tell me more?",
    "Sorry, I didn't catch that. Want to try again?"
]

# Rule-based smart reply function
def chatbot_response(message):
    msg = message.lower()

    if re.search(r"\b(hello|hi|hey)\b", msg):
        return random.choice(greetings)

    elif re.search(r"\b(bye|goodbye|see you)\b", msg):
        return random.choice(farewells)

    elif re.search(r"\b(how are you|how's it going)\b", msg):
        return "I'm doing great! Thanks for asking. How about you?"

    elif re.search(r"\b(nothing much|just chilling|relaxing)\b", msg):
        return "That sounds peaceful. 😊"

    elif re.search(r"\b(help|what can you do)\b", msg):
        return "I can greet you, remember your name, and chat a little. Try saying 'my name is...'"

    elif re.search(r"\b(thanks|thank you)\b", msg):
        return random.choice(thanks_replies)

    elif "my name is" in msg:
        name = msg.split("my name is")[-1].strip().capitalize()
        memory["name"] = name
        return f"Nice to meet you, {name}!"

    elif "what's my name" in msg or "who am i" in msg:
        return f"You're {memory.get('name', 'someone mysterious')}!"

    else:
        return random.choice(fallbacks)

# Chat loop
def chat():
    print("🤖 ChatBot: Hi! Type 'bye' or 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["bye", "exit"]:
            print("🤖 ChatBot:", random.choice(farewells))
            break
        time.sleep(0.4)
        response = chatbot_response(user_input)
        print("🤖 ChatBot:", response)

if __name__ == "__main__":
    chat()
