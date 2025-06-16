from tkinter import *
import pandas
import random
import os

# --- Global Variables ---
BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn = []
flip_timer = None


# --- Functions ---

def save_words_to_learn():
    """Saves the current list of words to learn into words_to_learn.csv."""
    df = pandas.DataFrame(to_learn)
    df.to_csv("./data/words_to_learn.csv", index=False)

def card_flip():
    """Flips the flashcard to display the English translation."""
    global current_card
    flash_card.itemconfig(card_image_id, image=card_back)
    flash_card.itemconfig(card_title, text="English", fill="white")
    flash_card.itemconfig(card_word, text=current_card["English"], fill="white")

def next_card():
    """Selects a new random card, updates the display, and sets a timer to flip the card."""
    global current_card, to_learn, flip_timer

    # Cancel any previous flip timer to prevent multiple timers running
    if flip_timer:
        window.after_cancel(flip_timer)

    # Update words left display
    update_words_left_display()

    if not to_learn:
        # Handle case where all words are learned
        flash_card.itemconfig(card_title, text="Congrats!", fill="green")
        flash_card.itemconfig(card_word, text="You learned all words!", fill="green")
        button_right.config(state=DISABLED)
        button_wrong.config(state=DISABLED)
        if os.path.exists("./data/words_to_learn.csv"):
            os.remove("./data/words_to_learn.csv")
        return

    current_card = random.choice(to_learn)

    flash_card.itemconfig(card_image_id, image=card_front)
    flash_card.itemconfig(card_title, text="French", fill="black")
    flash_card.itemconfig(card_word, text=current_card["French"], fill="black")

    # Set timer for card flip
    flip_timer = window.after(3000, card_flip)

def right_clicked():
    """Removes the current word from the learning list (user knows it) and moves to the next card."""
    global to_learn
    # Remove the current card from the list if it exists
    if current_card in to_learn:
        to_learn.remove(current_card)
    save_words_to_learn()
    next_card()

def wrong_clicked():
    """Moves to the next card without removing the current word (user doesn't know it)."""
    next_card()

def reset_progress():
    """Resets learning progress by reloading all words from the original French words file."""
    global to_learn
    if os.path.exists("./data/words_to_learn.csv"):
        os.remove("./data/words_to_learn.csv")

    # Reload from original french_words.csv
    try:
        data = pandas.read_csv("./data/french_words.csv")
        to_learn = data.to_dict(orient="records")
    except FileNotFoundError:
        print("Error: 'data/french_words.csv' not found. Cannot reset.")
        # Re-create dummy data if original not found
        data = pandas.DataFrame({
            "French": ["Bonjour", "Merci", "Au revoir", "Comment", "Soleil", "Eau"],
            "English": ["Hello", "Thank you", "Goodbye", "How", "Sun", "Water"]
        })
        to_learn = data.to_dict(orient="records")

    # Re-enable buttons if they were disabled
    button_right.config(state=NORMAL)
    button_wrong.config(state=NORMAL)
    next_card()

def update_words_left_display():
    """Updates the GUI label showing the count of words remaining to learn."""
    words_left_label.config(text=f"Words Left: {len(to_learn)}")


# --- Data Loading ---
# Prioritize loading words from words_to_learn.csv; fallback to french_words.csv
try:
    if os.path.exists("./data/words_to_learn.csv"):
        data = pandas.read_csv("./data/words_to_learn.csv")
    else:
        data = pandas.read_csv("./data/french_words.csv")
    to_learn = data.to_dict(orient="records")
except FileNotFoundError:
    print("Error: Neither 'data/words_to_learn.csv' nor 'data/french_words.csv' found. Using dummy data.")
    data = pandas.DataFrame({
        "French": ["Bonjour", "Merci", "Au revoir", "Comment", "Soleil", "Eau"],
        "English": ["Hello", "Thank you", "Goodbye", "How", "Sun", "Water"]
    })
    to_learn = data.to_dict(orient="records")


# --- Window Setup ---
window = Tk()
window.title("Flashy")
window.config(padx=70, pady=70, bg=BACKGROUND_COLOR)


# --- Image Assets ---
card_front = PhotoImage(file="./images/card_front.png")
card_back = PhotoImage(file="./images/card_back.png")
right_img = PhotoImage(file="./images/right.png")
wrong_img = PhotoImage(file="./images/wrong.png")


# --- Canvas for Flashcard ---
flash_card = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0, borderwidth=0)
card_image_id = flash_card.create_image(400, 270, image=card_front)
card_title = flash_card.create_text(400, 150, text="French", font=("Arial", 40, "italic"), fill="black")
card_word = flash_card.create_text(400, 260, text="Word", font=("Arial", 60, "bold"), fill="black")
flash_card.grid(row=0, column=0, columnspan=2)


# --- Buttons ---
button_wrong = Button(image=wrong_img, highlightthickness=0, bd=0, command=wrong_clicked)
button_right = Button(image=right_img, highlightthickness=0, bd=0, command=right_clicked)

button_wrong.grid(row=1, column=0, padx=20, pady=20)
button_right.grid(row=1, column=1, padx=20, pady=20)


# --- Progress Label ---
words_left_label = Label(text=f"Words Left: {len(to_learn)}", bg=BACKGROUND_COLOR, font=("Arial", 16))
words_left_label.grid(row=2, column=0, columnspan=2, pady=10)


# --- Reset Button ---
reset_button = Button(text="Reset Progress", command=reset_progress, font=("Arial", 14), bg="#ADD8E6", fg="black", padx=10, pady=5, relief="raised", bd=2)
reset_button.grid(row=3, column=0, columnspan=2, pady=10)


# --- Initial Card Display ---
next_card()

window.mainloop()
