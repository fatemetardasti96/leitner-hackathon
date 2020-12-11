import sqlite3
from typing import Optional, Tuple

from skill_sdk import skill, Response, tell, ask
from skill_sdk.l10n import _
from skill_sdk import context

import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

connection = sqlite3.connect('/assets/questions.db')

def initialize_db():
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, user_id VARCHAR (128) NOT NULL, quiz TEXT, answer TEXT,topic VARCHAR (100), step INTEGER DEFAULT 1)")
    cursor.execute("CREATE TABLE IF NOT EXISTS user_questions (id INTEGER PRIMARY KEY, questions_id INTEGER) ")
    connection.commit()    

initialize_db()
nltk.download('punkt')
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize)

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

def similar_answer(answer, text):
    return cosine_sim(answer, text)>0.7

class IntentNames:
    CREATE = "TEAM_12_CREATE_FLASHCARD"
    CREATE_QUESTION = "TEAM_12_FLASHCARD_QUESTION"
    CREATE_ANSWER = "TEAM_12_FLASHCARD_ANSWER"
    CREATE_TOPIC = "TEAM_12_FLASHCARD_TOPIC"

    REVIEW = "TEAM_12_FLASHCARD_REVIEW"
    REVIEW_ANSWER = "TEAM_12_FLASHCARD_REVIEW_ANSWER"

    STATISTIC = "TEAM_12_STATISTICS"

def create_question(user_id: str, quiz: str):
    cursor = connection.cursor()
    cursor.execute("insert into questions (user_id, quiz) values (?, ?) ", (user_id, quiz))
    connection.commit()

def get_last_quiz(user_id) -> Tuple:
    cursor = connection.cursor()
    cursor.execute("select id, quiz, answer, topic from questions where user_id = ? order by id desc limit 1", [user_id])
    question = cursor.fetchone()
    return question

@skill.intent_handler(IntentNames.CREATE)
def handle_create(user_id: str) -> Response:
    return ask(_("WHAT_IS_THE_QUESTION"))

@skill.intent_handler(IntentNames.CREATE_QUESTION)
def handle_create_question(user_id: str, quiz:str) -> Response:
    try:
        create_question(user_id, quiz)
    except Exception as err:
        return tell(_("something went wrong on the server"))
    return ask(_("WHAT_IS_THE_ANSWER"))


@skill.intent_handler(IntentNames.CREATE_ANSWER)
def handle_create_answer(user_id: str, answer:str) -> Response:
    try:
        question = get_last_quiz(user_id)
        if question is None or (question[0] and question[1] and question[2]):
            raise Exception()
        else:
            cursor = connection.cursor()
            question = get_last_quiz(user_id)
            cursor.execute("update questions set answer = ? where id = ?", [answer, question[0]])
            connection.commit()
    except Exception as err:
        return tell(_("something went wrong on the server"))
    return ask(_("WHAT_IS_THE_TOPIC"))


@skill.intent_handler(IntentNames.CREATE_TOPIC)
def handle_create_topic(user_id: str, topic:str) -> Response:
    try:
        question = get_last_quiz(user_id)
        if question is None or (question[0] and question[1] and question[2] and question[3]):
            raise Exception()
        else:
            cursor = connection.cursor()
            question = get_last_quiz(user_id)
            cursor.execute("update questions set topic = ? where id = ?", [topic, question[0]])
            connection.commit()
    except Exception as err:
        return tell(_("something went wrong on the server"))
    return tell(_("CARD_CREATED"))


@skill.intent_handler(IntentNames.REVIEW)
def handle_review(user_id: str, topic:str) -> Response:
    try:
        cursor = connection.cursor()
        question_id, quiz, answer, _ = cursor.execute("select questions.id, quiz, answer, max(user_questions.id) as max_id from questions left join\
            user_questions on questions.id = user_questions.questions_id where user_id = ? and topic = ? and step<6 group by questions.id \
            order by max_id limit 1", [user_id, topic]).fetchone()
        if quiz is None:
            msg = _("NO_MORE_QUIESTION")
            return tell(msg)
        cursor.execute("insert into user_questions (questions_id) values (?)", [question_id])
        connection.commit()     
    except Exception as err:
        return tell(_("something went wrong on the server"))
    return ask(quiz)


@skill.intent_handler(IntentNames.REVIEW_ANSWER)
def handle_review_answer(user_id: str, answer:str) -> Response:
    try:
        cursor = connection.cursor()
        last_question_id, correct_answer, step = cursor.execute("select questions_id, answer, step from user_questions uq\
        JOIN questions q on q.id = uq.questions_id where q.user_id = ? order by uq.id desc limit 1", [user_id]).fetchone()
        if similar_answer(answer, correct_answer):
            step += 1
            msg = _("CORRECT_ANSWER")
        else:
            step = max(1, step-1)
            msg = _("WRONG_ANSWER",correct_answer=correct_answer)
        cursor.execute("update questions set step = ? where id = ?", [step, last_question_id])        
        connection.commit()
    except Exception as err:
        return tell(_("something went wrong on the server"))
    return tell(msg)


@skill.intent_handler(IntentNames.STATISTIC)
def handler_statistic(user_id: str):
    cursor = connection.cursor()
    questions_cnt = cursor.execute("SELECT COUNT(*) as cnt FROM questions WHERE user_id = ? ", [user_id]).fetchone()
    completed_questions_cnt = cursor.execute("SELECT COUNT(*) as cnt FROM questions WHERE user_id = ? AND step = 5", [user_id]).fetchone()
    msg = _("STATISTIC", total_num=questions_cnt, comp_num=completed_questions_cnt)
    return tell(msg)
