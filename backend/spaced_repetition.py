"""
Simplified SM-2 Spaced Repetition Algorithm
--------------------------------------------
Every time a user reviews a flashcard, they rate how well they remembered it:
    0 - Again (forgot completely)
    1 - Hard (remembered with difficulty)
    2 - Good (remembered correctly)
    3 - Easy (remembered instantly)

Based on this rating, we calculate:
    - new interval (days until next review)
    - new ease_factor (how "easy" this card is for the user)
    - new repetitions count
"""

from datetime import datetime, timedelta


def calculate_next_review(quality, repetitions, ease_factor, interval):
    """
    quality: int (0-3) - how well the user remembered the card
    repetitions: int - number of times reviewed correctly in a row
    ease_factor: float - current ease factor of the card (min 1.3)
    interval: int - current interval in days

    Returns: (new_repetitions, new_ease_factor, new_interval, next_review_date)
    """

    # If the user forgot the card, reset progress
    if quality == 0:
        repetitions = 0
        interval = 1
    else:
        # Update ease factor based on quality (SM-2 formula, simplified)
        ease_factor = ease_factor + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        repetitions += 1

        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = round(interval * ease_factor)

    next_review_date = datetime.now() + timedelta(days=interval)

    return repetitions, round(ease_factor, 2), interval, next_review_date
