from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Blueprint, render_template

from module1.global_variable import annotation_progress, q_cache, TOTAL_TASK_NUM
from module1.helper import setValue, getValue, preprocess, tmp, get_annotation_progress, tmp2, cos_two_sentences, \
    get_policy_by_prolific_id
# from module1.main import annotation_progress
from module1.models import CoronaNet
from nltk.corpus import stopwords
from flask import request
from module1 import db, MANUAL_POLICY_ID, model2, tokenizer, model, nlp

import numpy.linalg as LA
import numpy as np
import torch
import json
import re

bp_annotation = Blueprint('annotation', __name__)

# q_cache = {}  # policy's json object cache
# p_cache = {}  # policy's text cache

'''
record how many questions have been saved, key is policy_id, value is a 2-d array

'''
# annotation_progress = {}


@bp_annotation.route("/annotation/<int:policy_id>/<int:question_id>", methods=['GET', 'POST'])
def get_annotation(policy_id, question_id):
    if policy_id < 1 or policy_id > MANUAL_POLICY_ID * 2:
        return "Policy {} is not found.".format(policy_id)

    if policy_id < MANUAL_POLICY_ID:
        return get_annotation_manual(policy_id, question_id)
    else:
        return get_annotation_AI(policy_id, question_id)


def get_selection_manual(policy_id, question_id):
    if policy_id not in q_cache.keys():
        with open('./module1/static/questions.json', encoding="utf8") as f:
            q_objs = json.load(f)
            q_cache[policy_id] = q_objs
        annotation_progress[policy_id] = {}
    else:
        q_objs = q_cache[policy_id]

    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    has_answer = False

    qt = None
    for q in q_objs:
        db_column_name = q["columnName"]
        obj_property = getValue(policy, db_column_name)

        if q["id"] == question_id:
            if q["taskType"] == 1:
                qt = q
                options_list = []
                for option in q["options"]:
                    if not option["isTextEntry"]:
                        options_list.append(option["option"] if option["note"] == "" else option["note"])

                if obj_property is None or obj_property == "":
                    pass
                else:
                    q["answers"] = obj_property
                    has_answer = True

                if has_answer:
                    for option in q["options"]:
                        if "[Text entry]" in option["option"] and "[Text entry]" in q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            q["answers"] = q["answers"].split("|")[0]
                            break
                        elif option["option"] == q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            break
                q["has_answer"] = has_answer
            break

    graph_list = get_policy_obj(policy.original_text)
    a, b = get_annotation_progress(policy_id, q_objs)
    return render_template('annotation_manual.html',
                           policy=policy,
                           question_id=question_id,
                           summary_list=[],
                           graph_list=graph_list,
                           q=qt,
                           annotation_progress=annotation_progress[policy_id],
                           complete=a,
                           total=b,
                           pre=question_id - 1,
                           next=question_id + 1)


def get_completation_manual(policy_id, question_id):
    if policy_id not in q_cache.keys():
        with open('./module1/static/questions.json', encoding="utf8") as f:
            q_objs = json.load(f)
            q_cache[policy_id] = q_objs
        annotation_progress[policy_id] = {}
    else:
        q_objs = q_cache[policy_id]

    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    has_answer = False

    qt = None
    for q in q_objs:
        db_column_name = q["columnName"]
        obj_property = getValue(policy, db_column_name)

        if q["id"] == question_id:
            if q["taskType"] == 2:
                qt=q
                if obj_property is None or obj_property == "":
                    pass
                else:
                    q["answers"] = obj_property
                    has_answer = True
                q["has_answer"] = has_answer
            break

    graph_list = get_policy_obj(policy.original_text)
    a, b = get_annotation_progress(policy_id, q_objs)
    return render_template('annotation_manual.html',
                           policy=policy,
                           question_id=question_id,
                           summary_list=[],
                           graph_list=graph_list,
                           q=qt,
                           annotation_progress=annotation_progress[policy_id],
                           complete=a,
                           total=b,
                           pre=question_id - 1,
                           next=question_id + 1)


def get_selection_AI(policy_id, question_id, q):
    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    db_column_name = q["columnName"]
    db_column_answer = getattr(policy, db_column_name)
    has_answer = False

    options_list = []
    for option in q["options"]:
        if not option["isTextEntry"]:
            options_list.append(option["option"] if option["note"] == "" else option["note"])
    q["AI_QA_result"] = multi_choice_QA(policy.original_text, options_list)[0]
    m_cos = 0
    arr = q["AI_QA_result"].tolist()
    max_cos = max(arr)

    if db_column_answer is None or db_column_answer == "":
        for option in q["options"]:
            if m_cos == option["cos"]:
                q["answers"] = option["option"]
    else:
        q["answers"] = db_column_answer
        has_answer = True

    if has_answer:
        for i in range(0, len(q["AI_QA_result"])):
            q["options"][i]["cos"] = q["AI_QA_result"][i]
        for option in q["options"]:
            if option["cos"] == max_cos:
                option["type"] = 2
                break
        for option in q["options"]:
            if "[Text entry]" in option["option"] and "[Text entry]" in q["answers"]:
                option["checked"] = "True"
                option["type"] = 1
                q["answers"] = q["answers"].split("|")[0]
                break
            elif option["option"] == q["answers"]:
                option["checked"] = "True"
                option["type"] = 1
                break
        graph_list = get_highlight_sentences_obj(policy_id, q["answers"])
    else:
        for i in range(0, len(q["AI_QA_result"])):
            q["options"][i]["cos"] = q["AI_QA_result"][i]
            if q["AI_QA_result"][i] == max_cos:
                q["options"][i]["checked"] = "True"

        for option in q["options"]:
            if option["cos"] == max_cos:
                option["checked"] = "True"
                option["type"] = 2
                graph_list = get_highlighting_text_base_obj(policy_id, question_id, option["id"])
                break
    q["has_answer"] = has_answer

    summary_list = get_policy_obj(policy.original_text)
    return policy, summary_list, graph_list


def get_completation_AI(policy_id, question_id, q):
    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    db_column_name = q["columnName"]
    db_column_answer = getattr(policy, db_column_name)
    q["answers"], graph_list = tmp2(q["columnName"], policy_id, q["question"], q["clarification"])
    if db_column_answer is None or db_column_answer == "":
        q["has_answer"] = False
    else:
        q["has_answer"] = True
        q["AI_answer"] = db_column_answer

    summary_list = get_policy_obj(policy.original_text)
    return policy, summary_list, graph_list


def get_annotation_AI(policy_id, question_id):
    if policy_id not in q_cache.keys():
        with open('./module1/static/questions.json', encoding="utf8") as f:
            q_objs = json.load(f)
            q_cache[policy_id] = q_objs
        annotation_progress[policy_id] = {}
    else:
        q_objs = q_cache[policy_id]

    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    context = preprocess(policy.original_text)
    has_answer = False

    questions = []

    for q in q_objs:
        db_column_name = q["columnName"]
        db_column_answer = getattr(policy, db_column_name)

        if q["id"] == question_id:
            print(q["id"])
            if q["taskType"] == 1:
                options_list = []
                for option in q["options"]:
                    if not option["isTextEntry"]:
                        options_list.append(option["option"] if option["note"] == "" else option["note"])
                q["AI_QA_result"] = multi_choice_QA(policy.original_text, options_list)[0]
                m_cos = 0
                arr = q["AI_QA_result"].tolist()
                max_cos = max(arr)

                if db_column_answer is None or db_column_answer == "":
                    for option in q["options"]:
                        if m_cos == option["cos"]:
                            q["answers"] = option["option"]
                else:
                    q["answers"] = db_column_answer
                    has_answer = True

                if has_answer:
                    for i in range(0, len(q["AI_QA_result"])):
                        q["options"][i]["cos"] = q["AI_QA_result"][i]
                    for option in q["options"]:
                        if option["cos"] == max_cos:
                            option["type"] = 2
                            break
                    for option in q["options"]:
                        if "[Text entry]" in option["option"] and "[Text entry]" in q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            q["answers"] = q["answers"].split("|")[0]
                            break
                        elif option["option"] == q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            break
                    graph_list = get_highlight_sentences_obj(policy_id, q["answers"])
                else:
                    for i in range(0, len(q["AI_QA_result"])):
                        q["options"][i]["cos"] = q["AI_QA_result"][i]
                        if q["AI_QA_result"][i] == max_cos:
                            q["options"][i]["checked"] = "True"

                    for option in q["options"]:
                        if option["cos"] == max_cos:
                            option["checked"] = "True"
                            option["type"] = 2
                            graph_list = get_highlighting_text_base_obj(policy_id, question_id, option["id"])
                            break
                q["has_answer"] = has_answer
            elif q["taskType"] == 2:
                q["answers"], graph_list = tmp(q["columnName"], policy_id)
                if db_column_answer is None or db_column_answer == "":
                    q["has_answer"] = False
                else:
                    q["has_answer"] = True
                    q["AI_answer"] = db_column_answer
            questions.append(q)
            break

    summary_list = get_policy_obj(policy.original_text)
    a, b = get_annotation_progress(policy_id, q_objs)
    return render_template('annotation.html',
                           policy=policy,
                           questions=questions,
                           summary_list=summary_list,
                           graph_list=graph_list,
                           annotation_progress=annotation_progress[policy_id],
                           complete=a,
                           total=b,
                           pre=question_id - 1,
                           next=question_id + 1)


def get_annotation_manual(policy_id, question_id):
    # global q_cache

    if policy_id not in q_cache.keys():
        with open('./module1/static/questions.json', encoding="utf8") as f:
            q_objs = json.load(f)
            q_cache[policy_id] = q_objs
        annotation_progress[policy_id] = {}
    else:
        q_objs = q_cache[policy_id]

    policy = CoronaNet.query.filter_by(policy_id=policy_id).first()
    has_answer = False

    # qqqqq = []

    for q in q_objs:
        db_column_name = q["columnName"]
        obj_property = getValue(policy, db_column_name)

        if q["id"] == question_id:
            if q["taskType"] == 1:
                options_list = []
                for option in q["options"]:
                    if not option["isTextEntry"]:
                        options_list.append(option["option"] if option["note"] == "" else option["note"])

                if obj_property is None or obj_property == "":
                    pass
                else:
                    q["answers"] = obj_property
                    has_answer = True

                if has_answer:
                    for option in q["options"]:
                        if "[Text entry]" in option["option"] and "[Text entry]" in q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            q["answers"] = q["answers"].split("|")[0]
                            break
                        elif option["option"] == q["answers"]:
                            option["checked"] = "True"
                            option["type"] = 1
                            break
                else:
                    pass
                q["has_answer"] = has_answer
            elif q["taskType"] == 2:
                if obj_property is None or obj_property == "":
                    pass
                else:
                    q["answers"] = obj_property
                    has_answer = True
                q["has_answer"] = has_answer
            # qqqqq.append(q)
            break

    # summary_list = get_policy_obj(policy.description)
    graph_list = get_policy_obj(policy.original_text)
    a, b = get_annotation_progress(policy_id, q_objs)
    return render_template('annotation_manual.html',
                           policy=policy,
                           question_id=question_id,
                           summary_list=[],
                           graph_list=graph_list,
                           annotation_progress=annotation_progress[policy_id],
                           complete=a,
                           total=b,
                           pre=question_id - 1,
                           next=question_id + 1)


def get_option_text_by_qid(policy_id, question_id, option_id):
    questions = q_cache[int(policy_id)]
    for question in questions:
        if question["id"] == int(question_id):
            options = question["options"]
            for option in options:
                if option["id"] == option_id:
                    return option["option"], option["note"]


@bp_annotation.route("/policies/<int:q_type>/save", methods=['POST'])
def save(q_type):
    dataJson = request.data.decode("utf-8")
    data = json.loads(dataJson)

    policy = db.session.query(CoronaNet).filter_by(policy_id=data["pid"]).first()

    policy = setValue(policy, data['column'], data['answer'])
    db.session.commit()

    # clear the cache
    # global q_cache
    # global annotation_progress
    q_objs = q_cache[int(data["pid"])]

    for q in q_objs:
        if q["columnName"] == data['column']:
            if q_type == 1:
                for op in q["options"]:
                    if '[Text entry]' in op['option'] and '[Text entry]' in data['answer']:
                        op['checked'] = "True"
                    elif op['option'] == data['answer']:
                        op['checked'] = "True"
                    else:
                        op['checked'] = "False"
            else:
                if q["columnName"] == data['column']:
                    q["answers"] = data['answer']
                    q["has_answer"] = True

    pid = int(data["pid"])
    qid = int(data["qid"])
    annotation_progress[pid][qid] = True
    a, b = get_annotation_progress(pid, q_objs)
    return json.dumps({'success': True, 'complete': a, 'total': b}), 200, {'ContentType': 'application/json'}


@bp_annotation.route("/policies/save2", methods=['POST'])
def save2():
    dataJson = request.data.decode("utf-8")
    data = json.loads(dataJson)

    policy = db.session.query(CoronaNet).filter_by(policy_id=data["pid"]).first()

    policy = setValue(policy, data['column'], data['answer'])
    db.session.commit()

    # clear the cache
    # global q_cache
    # global annotation_progress
    q_objs = q_cache[int(data["pid"])]

    for q in q_objs:
        if q["columnName"] == data['column']:
            q["answers"] = data['answer']
            q["has_answer"] = True

    pid = int(data["pid"])
    qid = int(data["qid"])
    annotation_progress[pid][qid] = True
    a, b = get_annotation_progress(pid, q_objs)
    return json.dumps({'success': True, 'complete': a, 'total': b}), 200, {'ContentType': 'application/json'}


@bp_annotation.route("/policies/highlighting", methods=['POST'])
def get_highlighting_text():
    data = request.data.decode("utf-8")
    data = data.split("------")

    return get_highlighting_text_base(data[0], data[1], data[2])


def get_highlighting_text_base(policy_id, question_id, option_id):
    option_text = get_option_text_by_qid(policy_id, question_id, option_id)

    global p_cache
    if question_id in p_cache.keys():
        pass
    else:
        p_cache[question_id] = get_highlight_sentences(policy_id, option_text)

    return p_cache[question_id]


def get_highlighting_text_base_obj(policy_id, question_id, option_id):
    option_text, note_text = get_option_text_by_qid(policy_id, question_id, option_id)

    if policy_id % 2 == 0:
        option_text = "Closure and Regulations of Schools."

    return get_highlight_sentences_obj(policy_id, option_text)


def get_highlight_sentences(policy_id, option_text):
    policy_text = json.dumps(get_highlight_sentences_obj(policy_id, option_text))
    return policy_text


def get_highlight_sentences_obj(policy_id, option_text):
    policy_original_text = CoronaNet.query.filter_by(policy_id=policy_id).first().__dict__
    policy_graphs = policy_original_text["original_text"]
    policy_graphs = policy_graphs.replace('\n\n', '\n').split('\n')

    g_id = 0  # the index of a graph
    g_dic = {}
    for g in policy_graphs:
        sep = '.'
        sentences = [x + sep for x in g.split(sep)]
        try:
            sentences.remove('.')
        except:
            pass

        s_id = 0  # the index of a sentence in a graph
        g_dic[g_id] = []

        for s in sentences:
            s.replace("..", ".")
            score = cos_two_sentences(option_text, s)
            g_dic[g_id].append({"sentence_id": s_id, "sentence": s, "score": score})
            s_id = s_id + 1
        g_id = g_id + 1
    return g_dic


def filter_answer_by_consine_similarity(s1, s2):
    sentence_embeddings = model2.encode([s1, s2])
    score = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])[0][0]
    if score >= 0.5:
        return True
    else:
        return False


def signle_QA2(question, context):
    inputs = tokenizer.encode_plus(question, context, return_tensors="pt")
    answer_start_scores, answer_end_scores = model(**inputs)
    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1
    answer = tokenizer.convert_tokens_to_string(
        tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])).replace('[CLS]', '')

    if '[SEP]' in answer:
        answer = (answer.split('[SEP]')[1]).strip()

    if answer not in context:
        return ""
    return answer


def signle_QA(question, context):
    QA_input = {
        'question': question,
        'context': context
    }
    res = nlp(QA_input)

    return res['answer']


def multi_QA(question, graph_list):
    answers = set([])
    for graph in graph_list:
        for context in graph:
            if context == '':
                continue

            answer = signle_QA(question, context)
            if filter_answer_by_consine_similarity(question, answer):
                answers.add(answer)

        res = "|".join(answers)
    return res


def multi_choice_QA(policy, options_list):
    options_list.insert(0, policy)
    # Encoding:
    sentence_embeddings = model2.encode(options_list)
    # sentence_embeddings.shape

    # let's calculate cosine similarity for sentence 0:
    res = cosine_similarity(
        [sentence_embeddings[0]],
        sentence_embeddings[1:]
    )
    return res


def get_policy_obj(policy):
    i = 0
    j = 0
    res = []
    graph_list = policy.split('\n')
    for g in graph_list:
        sentence_list = re.split('(?<=[.!?]) +', g)
        sentence_dic = {}
        for s in sentence_list:
            sentence_dic["s" + str(i)] = s
            i += 1
        res.append(sentence_dic)
        j += 1
    return res


def max_cos(option, answers):
    max = 0
    answers = answers.split('|')
    for answer in answers:
        c = cos(option, answer)
        if c > max:
            max = c

    return max


def cos(s1, s2):
    cosine = 0

    options = []
    answers = []

    options.append(s1)
    answers.append(s2)

    if len(options) > 0 and len(answers) > 0:
        stopWords = stopwords.words('english')
        vectorizer = CountVectorizer(stop_words=stopWords)

        s1 = vectorizer.fit_transform(options).toarray()[0]
        s2 = vectorizer.transform(answers).toarray()[0]

        cosine = consine_cal(s1, s2)

    return cosine


def consine_cal(v1, v2):
    a = np.inner(v1, v2)
    b = LA.norm(v1) * LA.norm(v2)
    if a == 0 or b == 0:
        return 0

    return round(a / b, 3)


@bp_annotation.route("/policies/<string:prolific_id>/view", methods=['GET', 'POST'])
def view(prolific_id):
    policy_tmp = get_policy_by_prolific_id(prolific_id)

    policy = {}
    policy['description'] = policy_tmp.description
    policy['type'] = policy_tmp.type
    policy['country'] = policy_tmp.country

    cnt = 0
    for k in policy:
        if policy[k] is not None:
            cnt = cnt + 1

    ending = ''
    if cnt == TOTAL_TASK_NUM:
        ending = 'You have done all the tasks! Thanks!'

    return render_template('view.html', policy=policy, prolific_id=policy_tmp.prolific_id, ending=ending)



