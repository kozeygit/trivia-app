from itertools import cycle
import random
import json
from pathlib import Path


class Question:
    with open("trivia_questions.json", encoding="utf8") as file:
        json_data = file.read()
    ALL_QUESTIONS = json.loads(json_data)

    def __init__(self):
        self.question_dict = {}
        self.new_question()


    def new_question(self):
        self.question_dict = random.choice(Question.ALL_QUESTIONS)

    def new_random_questions(self, amount=None, category=None, difficulty=None, type=None):
        
        questions = self.ALL_QUESTIONS

        if category:
            questions = [question for question in questions if question["category"].lower() == category.lower()]

        if difficulty:
            questions = [question for question in questions if question["difficulty"].lower() == difficulty.lower()]

        if type:
            questions = [question for question in questions if question["type"].lower() == type.lower()]

        if amount: 
            self.random_questions = random.sample(questions, amount)
        else:
            self.random_questions = questions
        

    def get_random_questions(self, new=False, amount=None, category=None, difficulty=None, type=None):
        if new:
            self.new_random_questions(amount=amount, category=category, difficulty=difficulty, type=type)

        return self.random_questions

    def get_question(self):
        for i in self.question_dict:
            data = self.question_dict[i]
            print(f"{i}: {data}")

        

q = Question()

[print(f"\n{i}") for i in q.get_random_questions(new=True, amount=None, difficulty="hard", type="boolean")]
