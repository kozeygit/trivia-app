# research room to make a buzzer page where 2 phones
# will act as buzzers, need to find out how to differentiate
# the two phones, probably by a team name they type in
# able to buzz controlled by controller
# one phone buzz locks out the other phone
# show visual on screen of who buzzed


from flask import Flask, render_template, request, session, url_for, redirect
from flask_socketio import SocketIO, join_room, leave_room, close_room
from game_logic import Question, Round, generate_id

# Creates the flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

buzzers = {}

game_round = Round()


@app.route("/presenter/")
def presenter():
    return render_template(
        "presenter.html",
        title="Fortunate Families - Presenter",
        question=game_round.get_question(),
        answers=game_round.get_answers(),
        wrong_answers=game_round.wrong_answers,
        question_revealed=game_round.question_revealed,
        correct_answers=game_round.correct_answers,
        total_points=game_round.total_points,
    )


@app.route("/controller/")
def controller():
    return render_template(
        "controller.html",
        title="Fortunate Families - Controller",
        question=game_round.get_question(),
        answers=game_round.get_answers(),
        wrong_answers=game_round.wrong_answers,
        question_revealed=game_round.question_revealed,
        correct_answers=game_round.correct_answers,
        total_points=game_round.total_points,
    )


@app.route("/", methods=["POST", "GET"])
@app.route("/join/", methods=["POST", "GET"])
def join_team():
    session.clear()
    if request.method == "POST":

        c = request.form.get("controller", False)
        p = request.form.get("presenter", False)
        
        if c != False:
            return redirect(url_for("controller"))
        
        if p != False:
            return redirect(url_for("presenter"))
        
        team_name = request.form.get("team_name").upper()

        if team_name == "":
            return render_template("join.html", error="Please enter team name")

        if team_name not in buzzers:
            buzzers[team_name] = {"members": 0}

        session["team_name"] = team_name
        return redirect(url_for("buzzer"))

    return render_template("join.html")


@app.route("/buzzer/")
def buzzer():
    team_name = session.get("team_name")
    if team_name == None or team_name not in buzzers:
        return redirect(url_for("join_team"))
    return render_template("buzzer.html", team_name=team_name)


@socketio.on("connect")
def test_connect(auth):
    team_name = session.get("team_name")

    if not team_name:
        return
    if team_name not in buzzers:
        leave_room(team_name)
        return

    buzzers[team_name]["members"] += 1
    join_room(team_name)


@socketio.on("disconnect")
def disconnect():
    print("\n\n\n DISCONNECTED~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n\n")
    team_name = session.get("team_name")
    print(team_name)
    leave_room(team_name)

    if team_name in buzzers:
        buzzers[team_name]["members"] -= 1

        ##Breaks the saving of session when reloading on chrome browser
        # if buzzers[team_name]["members"] <= 0:
        #     del buzzers[team_name]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("buzz")
def activate_buzzer(time):
    team_name = session.get("team_name")
    if (not team_name) or (team_name not in buzzers):
        print("Buzzer has no team, please reload")
        return

    if game_round.buzzers_active:
        game_round.deactivate_buzzers()
        socketio.emit("buzz_in", team_name)
        socketio.emit("buzz_return", room=team_name)
        handle_get_buzzer_state()
        handle_play_sound(sound="buzz")
        print("\n\n\n")
        print(buzzers)
        print("team", session.get("team_name"), "buzzed in at", time)
        print("\n\n\n")

    else:
        print("Buzzers are not activated")

        for i in buzzers.items():
            print("\n", i, "\n")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("play_sound")
def handle_play_sound(sound, override=False):
    args = {"sound": sound, "override": override}
    socketio.emit("play_sound", args)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("get_round_data")
def handle_get_round_data():
    return_value = {
        "wrong_answers": game_round.wrong_answers,
        "total_points": game_round.total_points,
        "question_revealed": game_round.question_revealed,
        "answers_revealed": game_round.correct_answers,
        "round_over": game_round.round_over,
    }
    # socketio.emit("give_round_data", data=return_value)
    socketio.emit("give_wrong_answers", data=game_round.wrong_answers)
    socketio.emit("give_total_points", data=game_round.total_points)
    socketio.emit("give_question_revealed", data=game_round.question_revealed)
    socketio.emit("give_answers_revealed", data=game_round.correct_answers)
    socketio.emit("give_round_over", data=game_round.round_over)
    socketio.emit("give_buzzer_state", data=game_round.buzzers_active)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("get_wrong_answers")
def handle_get_wrong_answers():
    return_value = game_round.wrong_answers
    socketio.emit("give_wrong_answers", data=return_value)


@socketio.on("get_total_points")
def handle_get_total_points():
    return_value = game_round.total_points
    socketio.emit("give_total_points", data=return_value)


@socketio.on("get_question_revealed")
def handle_get_question_revealed():
    return_value = game_round.question_revealed
    socketio.emit("give_question_revealed", data=return_value)


@socketio.on("get_answers_revealed")
def handle_get_answers_revealed():
    return_value = game_round.correct_answers
    socketio.emit("give_answers_revealed", data=return_value)


@socketio.on("get_round_over")
def handle_get_round_over():
    return_value = game_round.round_over
    socketio.emit("give_round_over", data=return_value)


@socketio.on("get_buzzer_state")
def handle_get_buzzer_state():
    return_value = game_round.buzzers_active
    socketio.emit("give_buzzer_state", data=return_value)

    for i in buzzers:
        print(i, "\n")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("controller_new_question")
def controller_new_question():
    current_question_revealed = game_round.question_revealed
    game_round.new_round()
    if current_question_revealed:
        handle_play_sound("new_round")
        socketio.emit("presenter_new_question")
    else:
        handle_get_round_data()
        handle_get_current_question()


@socketio.on("controller_reveal_question")
def controller_reveal_question():
    if not game_round.question_revealed:
        game_round.question_revealed = True
        handle_get_question_revealed()


@socketio.on("controller_reveal_answer")
def controller_reveal_answer(answer_num):
    if game_round.correct_answers[answer_num]:
        print("Answer already revealed")
        return

    socketio.emit("presenter_reveal_answer", answer_num)
    game_round.correct_answers[answer_num] = True

    if game_round.round_over == False:
        game_round.add_points(answer_num)

    # This stuff only activates when the round is over for the first cycle only
    if (
        all(game_round.correct_answers.values()) == True
    ) or game_round.wrong_answers >= 3:
        if game_round.round_over == False:
            handle_play_sound("round_over")
        game_round.round_over = True

    handle_get_total_points()
    handle_get_answers_revealed()

    if answer_num == 1:
        if game_round.round_over == False:
            handle_play_sound("top_answer", override=True)
        else:
            handle_play_sound("correct_answer", override=True)
    else:
        handle_play_sound("correct_answer", override=True)


@socketio.on("controller_wrong_answer")
def handle_controller_wrong_answer():
    game_round.wrong_answers += 1
    print(game_round.wrong_answers)
    handle_get_wrong_answers()
    handle_play_sound("wrong_answer")
    if game_round.wrong_answers == 4:
        handle_play_sound("round_over")
        game_round.round_over = True
    socketio.emit("presenter_wrong_answer")


@socketio.on("controller_set_buzzer_state")
def handle_controller_set_buzzer_state(state):
    if state:
        game_round.activate_buzzers()
    else:
        game_round.deactivate_buzzers()
        socketio.emit("presenter_close_buzzer_modal")
    handle_get_buzzer_state()

@socketio.on("buzz_whenever")
def handle_buzz_whenever():
    socketio.emit("presenter_buzz_whenever")
    handle_play_sound("wrong_answer")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@socketio.on("get_current_question")
def handle_get_current_question():
    return_value = {
        "question": game_round.get_question(),
        "answer1": game_round.get_answers(1),
        "answer2": game_round.get_answers(2),
        "answer3": game_round.get_answers(3),
        "answer4": game_round.get_answers(4),
        "answer5": game_round.get_answers(5),
    }
    socketio.emit("give_current_question", return_value)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")


"""

store on server:

    The question:
        question
        answers
        points

    Revealed Questions

    Wrong Answers

    Total Points for Round

    
TO DO:

Add buzzer that can activate whenever
Visible timer



"""
