import copy

from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST
import json


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id", None)

    if current_question_id == None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session["current_question_id"] = 0
        return bot_responses

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question != None:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(optId, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is not None and (0 <= current_question_id < len(PYTHON_QUESTION_LIST)):
        current_question = PYTHON_QUESTION_LIST[current_question_id]
        current_options = current_question["options"]
        try:
            optId = int(optId)  # Convert answer to an integer
        except ValueError:
            return False, "Answer must be an integer"
        if not 0 < optId <=4:
            return False, "Please enter correct option between 1-4 "
        elif current_question["answer"] == current_options[optId-1]:
            session["correct_answer_count"] = session.get("correct_answer_count", 0) + 1
            return True, ""
    return True, "Invalid question ID"


def get_next_question(current_question_id):
    if current_question_id is None:
        question_details = copy.deepcopy(PYTHON_QUESTION_LIST[0])
        question_details.pop("answer")
        return question_details, 0
    elif len(PYTHON_QUESTION_LIST) <= current_question_id:
        return None, -1
    else:
        next_question_id = current_question_id + 1
        nex_question_details = copy.deepcopy(PYTHON_QUESTION_LIST[current_question_id])
        nex_question_details.pop("answer")
        return nex_question_details, next_question_id


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    correct_answer_count = session.get("correct_answer_count")
    total_questions = len(PYTHON_QUESTION_LIST)

    percentage = (correct_answer_count / total_questions) * 100

    report_text = f"You scored: {correct_answer_count}/{total_questions} ({percentage:.2f}%)"
    session['current_question_id'] = None
    session['message_history'] = []
    session['correct_answer_count'] = 0
    session.save()
    return report_text
