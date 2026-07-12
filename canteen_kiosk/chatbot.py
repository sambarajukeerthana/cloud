# chatbot.py
import spacy

nlp = spacy.load("en_core_web_sm")

def detect_intent(user_input):
    doc = nlp(user_input.lower())

    if "order" in user_input or "buy" in user_input:
        return "place_order"
    elif "menu" in user_input or "available" in user_input:
        return "show_menu"
    elif "cancel" in user_input:
        return "cancel_order"
    elif "hello" in user_input or "hi" in user_input:
        return "greet"
    else:
        return "unknown"

def respond_to_input(user_input):
    intent = detect_intent(user_input)
    if intent == "place_order":
        return "Sure! You can browse the menu and add items to your cart."
    elif intent == "show_menu":
        return "Here's our menu. You can filter by category or price."
    elif intent == "cancel_order":
        return "Your order has been canceled."
    elif intent == "greet":
        return "Hello! How can I help you today?"
    else:
        return "Sorry, I didn't quite get that. Can you try rephrasing?"
