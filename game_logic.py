import json
from random import choice, randint
import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "questions/ff_questions.json")

class Question:
    file = open(filename, encoding='utf8') 
    json_data = file.read()
    file.close()
    
    ALL_QUESTIONS = json.loads(json_data)
    
    def __init__(self):
        self.question_dict = choice(Question.ALL_QUESTIONS)

    def get_question(self):
        return self.question_dict
    

class Round:
    def __init__(self):
        self.new_round()

    def new_round(self):
        q = Question()
        question = q.get_question()
        self.question = question['question']
        self.question_revealed = False
        
        self.answers = {1:question["answer1"], 2:question["answer2"], 3:question["answer3"], 4:question["answer4"], 5:question["answer5"]}
        self.correct_answers = {1:False,2:False,3:False,4:False,5:False,}
        self.wrong_answers = 0
        
        self.round_over = False

        self.total_points = 0

        self.buzzers_active = False

    def add_points(self, answer_num):
        self.total_points += self.answers[answer_num]['points']

    def get_question(self):
        return self.question
    
    def get_answers(self, answer=0):
        if answer:
            return self.answers[answer]
        else:
            return self.answers
        
    def activate_buzzers(self):
        self.buzzers_active = True
    
    def deactivate_buzzers(self):
        self.buzzers_active = False
        

def generate_id():
    return randint(1, 999)