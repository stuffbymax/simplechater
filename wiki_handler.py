import wikipedia

last_disambig_options = []

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
