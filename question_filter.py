import json
from random import choice, randint
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "filter_qs.json")

file = open(filename, encoding="utf8")
json_data = file.read()
file.close()

ALL_QUESTIONS = json.loads(json_data)

good_list = ALL_QUESTIONS.copy()

for i in ALL_QUESTIONS:
    print(i['question'])
    print(i['answer1'])
    print(i['answer2'])
    print(i['answer3'])
    print(i['answer4'])
    print(i['answer5'])
    print('\n\n')
    if input().lower() == "n":
        continue
    else:
        good_list.append(i)
        print("Added to good List")
    os.system('cls')

new_file = open("filter_qs.json", 'w')
new_file.write(json.dumps(good_list))