def log_conversation(user, bot, logfile="chat_log.txt"):
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"You: {user}\nBot: {bot}\n")
