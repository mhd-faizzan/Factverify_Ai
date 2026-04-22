import random
from datetime import datetime


MESSAGES = [
    "What fact shall we verify today?",
    "Ready to uncover the truth?",
    "Knowledge is power — let's find some!",
    "Every search brings us closer to truth",
    "Let's explore something fascinating!",
]


def get_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    return "Good Evening"


def get_display_name(first_name: str, last_name: str, email: str) -> str:
    if first_name:
        return f"{first_name[0].upper()}. {last_name}"
    return email.split("@")[0]


def random_message() -> str:
    return random.choice(MESSAGES)

