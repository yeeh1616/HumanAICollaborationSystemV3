from nltk.tokenize import word_tokenize, sent_tokenize
from flask import Blueprint, render_template

from module1.global_variable import q_cache, annotation_progress
from module1.helper import get_annotation_progress, cos_two_sentences
from module1.models import CoronaNet
from nltk.corpus import stopwords
from flask import request
from module1 import db, MANUAL_POLICY_ID

import json

bp_summary = Blueprint('summary', __name__)


# http://127.0.0.1:5000/summary/10
@bp_summary.route("/summary/<int:policy_id>", methods=['GET', 'POST'])
def get_summary(policy_id):
    if policy_id < 1 or policy_id > MANUAL_POLICY_ID * 2:
        return "Policy {} is not found.".format(policy_id)

    if policy_id < MANUAL_POLICY_ID:
        return get_summary_manual(policy_id)
    else:
        return get_summary_AI(policy_id)


def get_summary_manual(policy_id):
    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    return render_template('summary_manual.html', policy=policy)


def get_summary_AI(policy_id):
    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()

    text = policy.original_text
    stopWords = stopwords.words('english')
    stopWords = set(stopWords)
    words = word_tokenize(text)
    freqTable = dict()

    for word in words:
        word = word.lower()

        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    average = int(sumValues / len(sentenceValue))

    summary = ''

    if policy_id % 2 == 0:
        from module1.helper_tmp import get_highlighted_tmp
        summary, policy.highlighted_text = get_highlighted_tmp(sentences)
    else:
        summary, policy.highlighted_text = get_highlighted(sentences, sentenceValue, average, summary)

    summary = summary.replace('\r','').replace('\n', ' ')

    has_summary = False
    if policy.description == '' or policy.description == None:
        policy.description = summary
    else:
        has_summary = True
        policy.description

    return policy, has_summary


def get_highlighted(sentences, sentenceValue, average, summary):
    highlighted = []
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
            highlighted.append([sentence, True])
        else:
            highlighted.append([sentence, False])
    return summary, highlighted


@bp_summary.route("/policies/<int:q_type>/save_summary", methods=['POST'])
def save_summary(q_type):
    data = request.data.decode("utf-8").split("------")
    pid = int(data[0])
    summary = data[1]

    policy = db.session.query(CoronaNet).filter_by(policy_id=pid).first()
    policy.description = summary

    db.session.commit()

    q_objs = q_cache[pid]

    for q in q_objs:
        if q["taskType"] == 0:
            q["answers"] = summary
            q["has_answer"] = True
            break
    qid = 1
    annotation_progress[pid][qid] = True
    a, b = get_annotation_progress(pid, q_objs)
    return json.dumps({'success': True, 'complete': a, 'total': b}), 200, {'ContentType': 'application/json'}


@bp_summary.route("/policies/get_highlighting_text", methods=['GET', 'POST'])
def get_highlighting_text():
    data = request.data.decode("utf-8").split("------")
    policy_id = data[0]
    summary = data[1]

    return summary


@bp_summary.route("/policies/reload_summary", methods=['GET', 'POST'])
def reload_summary():
    policy_id = request.data.decode("utf-8")
    summary = ''

    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()

    text = policy.original_text
    stopWords = stopwords.words('english')
    stopWords = set(stopWords)
    words = word_tokenize(text)
    freqTable = dict()

    for word in words:
        word = word.lower()

        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(text)
    # sentences = re.split('; |. |\n', text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    average = int(sumValues / len(sentenceValue))

    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence

    return summary
