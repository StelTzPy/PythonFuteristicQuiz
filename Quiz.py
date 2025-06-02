import tkinter as tk
from tkinter import ttk
import openai
import pygame

# Replace with your actual OpenAI API key
openai.api_key = "Your-API"

questions = []
current_question_index = 0
score = 0
asked_questions = set()
difficulty = "easy"

# Initialize pygame mixer for music
pygame.mixer.init()

def play_music(file):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play(-1)  # loop indefinitely

root = tk.Tk()
root.title("Futuristic Quiz")
root.geometry("600x400")
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("clam")

# Frame background
style.configure("TFrame", background="#121212")
style.configure("TLabelFrame", background="#121212")

# Label styling
style.configure("TLabel",
                background="#121212",
                foreground="#00FFC6",
                font=("Segoe UI", 16))

# Button styling
style.configure("TButton",
                background="#00FFC6",
                foreground="#121212",
                font=("Segoe UI", 14, "bold"),
                borderwidth=0,
                padding=10)
style.map("TButton",
          background=[("active", "#00e0b0")],
          foreground=[("active", "#ffffff")])


def generate_question():
    global difficulty
    prompts = {
        "easy": "Generate a simple yes/no technology question for students under 18. Format: 'Question: <question> | Answer: <yes/no>'",
        "medium": "Generate a moderately challenging yes/no technology question for teens. Format: 'Question: <question> | Answer: <yes/no>'",
        "hard": "Generate a complex yes/no question about advanced technology or computer science concepts. Format: 'Question: <question> | Answer: <yes/no>'"
    }
    for _ in range(10):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompts[difficulty]},
                    {"role": "user", "content": "Generate the question now."}
                ]
            )
            result = response.choices[0].message["content"].strip()
            if "|" in result:
                question, answer = result.split("|")
                question = question.replace("Question:", "").strip()
                answer = answer.replace("Answer:", "").strip().lower()
                if question not in asked_questions:
                    asked_questions.add(question)
                    return question, answer
        except Exception as e:
            print(f"OpenAI error: {e}")
            break
    return "Is this a default question?", "yes"

def split_question(question, max_length=40):
    if len(question) <= max_length:
        return question, ""
    split_index = question.rfind(" ", 0, max_length) or max_length
    return question[:split_index], question[split_index:].strip()

# --- UI frames ---

menu_frame = ttk.Frame(root)
menu_frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(menu_frame, text="Select Difficulty", font=("Segoe UI", 24, "bold"))
title_label.pack(pady=30)

ttk.Button(menu_frame, text="Easy", command=lambda: start_quiz("easy")).pack(pady=10)
ttk.Button(menu_frame, text="Medium", command=lambda: start_quiz("medium")).pack(pady=10)
ttk.Button(menu_frame, text="Hard", command=lambda: start_quiz("hard")).pack(pady=10)

quiz_frame = ttk.Frame(root)

question_label_part1 = ttk.Label(quiz_frame, text="", font=("Segoe UI", 18))
question_label_part2 = ttk.Label(quiz_frame, text="", font=("Segoe UI", 18))
score_label = ttk.Label(quiz_frame, text="", font=("Segoe UI", 14))
button_frame = ttk.Frame(quiz_frame)

question_label_part1.pack(pady=5)
question_label_part2.pack(pady=5)
score_label.pack(pady=10)
button_frame.pack(pady=10)

true_button = ttk.Button(button_frame, text="True", command=lambda: answer_question("yes"))
false_button = ttk.Button(button_frame, text="False", command=lambda: answer_question("no"))
restart_button = ttk.Button(quiz_frame, text="Restart", command=lambda: restart_quiz())

true_button.pack(side=tk.LEFT, padx=10)
false_button.pack(side=tk.LEFT, padx=10)

def start_quiz(selected_difficulty):
    global difficulty, questions, current_question_index, score, asked_questions
    difficulty = selected_difficulty
    questions.clear()
    current_question_index = 0
    score = 0
    asked_questions.clear()
    for _ in range(5):
        q, a = generate_question()
        questions.append((q, a))
    menu_frame.pack_forget()
    quiz_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    true_button.pack(side=tk.LEFT, padx=10)
    false_button.pack(side=tk.LEFT, padx=10)
    restart_button.pack_forget()
    update_question()
    play_music("quiz_music.mp3")  # play quiz music

def answer_question(user_answer):
    global current_question_index, score
    if current_question_index < len(questions):
        correct_answer = questions[current_question_index][1]
        if user_answer.lower() == correct_answer:
            score += 1
        current_question_index += 1
        update_question()

def update_question():
    global current_question_index, score
    if current_question_index < len(questions):
        q = questions[current_question_index][0]
        part1, part2 = split_question(q)
        question_label_part1.config(text=part1)
        question_label_part2.config(text=part2)
        score_label.config(text=f"Score: {score}/{current_question_index}")
    else:
        question_label_part1.config(text="Quiz Over!")
        question_label_part2.config(text="")
        score_label.config(text=f"Final Score: {score}/5")
        true_button.pack_forget()
        false_button.pack_forget()
        restart_button.pack(pady=10)

def restart_quiz():
    start_quiz(difficulty)

# Start lobby music at launch
play_music("lobby_music.mp3")

root.mainloop()
