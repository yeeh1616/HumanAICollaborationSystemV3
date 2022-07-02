import re
from gensim import utils
from gensim.parsing import preprocess_string
from nltk import word_tokenize
from nltk.corpus import stopwords
from sqlalchemy import desc

from module1 import stop_words, wv, model_name, db
from module1.global_variable import annotation_progress, TOP_N, original_text
from module1.models import CoronaNet


def setValue(policy, columnName, answer):
    if columnName == 'policy_id':
        policy.policy_id = answer

    elif columnName == 'entry_type':
        policy.entry_type = answer

    elif columnName == 'correct_type':
        policy.correct_type = answer

    elif columnName == 'update_type':
        policy.update_type = answer

    elif columnName == 'update_level':
        policy.update_level = answer

    elif columnName == 'description':
        policy.description = answer

    elif columnName == 'date_announced':
        policy.date_announced = answer

    elif columnName == 'date_start':
        policy.date_start = answer

    elif columnName == 'date_end':
        policy.date_end = answer

    elif columnName == 'country':
        policy.country = answer

    elif columnName == 'ISO_A3':
        policy.ISO_A3 = answer

    elif columnName == 'ISO_A2':
        policy.ISO_A2 = answer

    elif columnName == 'init_country_level':
        policy.init_country_level = answer

    elif columnName == 'domestic_policy':
        policy.domestic_policy = answer

    elif columnName == 'province':
        policy.province = answer

    elif columnName == 'ISO_L2':
        policy.ISO_L2 = answer

    elif columnName == 'city':
        policy.city = answer

    elif columnName == 'type':
        policy.type = answer

    elif columnName == 'type_sub_cat':
        policy.type_sub_cat = answer

    elif columnName == 'type_text':
        policy.type_text = answer

    elif columnName == 'institution_status':
        policy.institution_status = answer

    elif columnName == 'target_country':
        policy.target_country = answer

    elif columnName == 'target_geog_level':
        policy.target_geog_level = answer

    elif columnName == 'target_region':
        policy.target_region = answer

    elif columnName == 'target_province':
        policy.target_province = answer

    elif columnName == 'target_city':
        policy.target_city = answer

    elif columnName == 'target_other':
        policy.target_other = answer

    elif columnName == 'target_who_what':
        policy.target_who_what = answer

    elif columnName == 'target_direction':
        policy.target_direction = answer

    elif columnName == 'travel_mechanism':
        policy.travel_mechanism = answer

    elif columnName == 'compliance':
        policy.compliance = answer

    elif columnName == 'enforcer':
        policy.enforcer = answer

    elif columnName == 'dist_index_high_est':
        policy.dist_index_high_est = answer

    elif columnName == 'dist_index_med_est':
        policy.dist_index_med_est = answer

    elif columnName == 'dist_index_low_est':
        policy.dist_index_low_est = answer

    elif columnName == 'dist_index_country_rank':
        policy.dist_index_country_rank = answer

    elif columnName == 'link':
        policy.link = answer

    elif columnName == 'date_updated':
        policy.date_updated = answer

    elif columnName == 'recorded_date':
        policy.recorded_date = answer

    elif columnName == 'original_text':
        policy.original_text = answer

    elif columnName == 'status':
        policy.status = answer

    return policy


def getValue(policy, columnName):
    res = None

    if columnName == 'policy_id':
        res = policy.policy_id

    elif columnName == 'entry_type':
        res = policy.entry_type

    elif columnName == 'correct_type':
        res = policy.correct_type

    elif columnName == 'update_type':
        res = policy.update_type

    elif columnName == 'update_level':
        res = policy.update_level

    elif columnName == 'description':
        res = policy.description

    elif columnName == 'date_announced':
        res = policy.date_announced

    elif columnName == 'date_start':
        res = policy.date_start

    elif columnName == 'date_end':
        res = policy.date_end

    elif columnName == 'country':
        res = policy.country

    elif columnName == 'ISO_A3':
        res = policy.ISO_A3

    elif columnName == 'ISO_A2':
        res = policy.ISO_A2

    elif columnName == 'init_country_level':
        res = policy.init_country_level

    elif columnName == 'domestic_policy':
        res = policy.domestic_policy

    elif columnName == 'province':
        res = policy.province

    elif columnName == 'ISO_L2':
        res = policy.ISO_L2

    elif columnName == 'city':
        res = policy.city

    elif columnName == 'type':
        res = policy.type

    elif columnName == 'type_sub_cat':
        res = policy.type_sub_cat

    elif columnName == 'type_text':
        res = policy.type_text

    elif columnName == 'institution_status':
        res = policy.institution_status

    elif columnName == 'target_country':
        res = policy.target_country

    elif columnName == 'target_geog_level':
        res = policy.target_geog_level

    elif columnName == 'target_region':
        res = policy.target_region

    elif columnName == 'target_province':
        res = policy.target_province

    elif columnName == 'target_city':
        res = policy.target_city

    elif columnName == 'target_other':
        res = policy.target_other

    elif columnName == 'target_who_what':
        res = policy.target_who_what

    elif columnName == 'target_direction':
        res = policy.target_direction

    elif columnName == 'travel_mechanism':
        res = policy.travel_mechanism

    elif columnName == 'compliance':
        res = policy.compliance

    elif columnName == 'enforcer':
        res = policy.enforcer

    elif columnName == 'dist_index_high_est':
        res = policy.dist_index_high_est

    elif columnName == 'dist_index_med_est':
        res = policy.dist_index_med_est

    elif columnName == 'dist_index_low_est':
        res = policy.dist_index_low_est

    elif columnName == 'dist_index_country_rank':
        res = policy.dist_index_country_rank

    elif columnName == 'link':
        res = policy.link

    elif columnName == 'date_updated':
        res = policy.date_updated

    elif columnName == 'recorded_date':
        res = policy.recorded_date

    elif columnName == 'original_text':
        res = policy.original_text

    elif columnName == 'status':
        res = policy.status

    return res

def preprocess(text):
    '''
    1. First, split text into graph list
    2. Second, split graph into sentence list
    3. Finally, return graph list = [[sentence1, sentence2, ...],[sentence1, sentence2, ...],...]
    '''

    graph_list = []
    graph_list1 = text.split('\n')

    for g in graph_list1:
        sentence_list1 = re.split('(?<=[.!?]) +', g)
        sentence_list2 = []

        for s in sentence_list1:
            if s != '':
                sentence_list2.append(s)
        if len(sentence_list2) > 0:
            graph_list.append(sentence_list2)

    return graph_list


def w2v_sentence(word, sentence):
    '''
    Split the sentence into word list, and then get a cosine similarity list (word vs. each of words of the sentence)
    :param word:
    :param sentence:
    :return:
    '''
    word_list = utils.simple_preprocess(sentence)
    pairs = []
    for w in word_list:
        pairs.append((word, w))

    res = []
    for w1, w2 in pairs:
        if w2 in stop_words:
            continue

        try:
            score = wv.similarity(w1, w2)
            score = str(score)[0:4]
            score = float(score)
            res.append((w2, score))
        except:
            pass
        # print('%r\t%r\t%.2f' % (w1, w2, wv.similarity(w1, w2)))

    res.sort(reverse=True, key=lambda y: y[1])
    res = res[:TOP_N]
    return res


def cos_two_sentences(X, Y):
    # tokenization
    X_list = word_tokenize(X)
    Y_list = word_tokenize(Y)

    # sw contains the list of stopwords
    sw = stopwords.words('english')
    l1 = [];
    l2 = []

    # remove stop words from the string
    X_set = {w for w in X_list if not w in sw}
    Y_set = {w for w in Y_list if not w in sw}

    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    cosine = float(str(cosine)[0:4])
    return cosine


def tmp(column_name, policy_id):
    policy_original_text = CoronaNet.query.filter_by(policy_id=policy_id).first().__dict__
    policy_graphs = policy_original_text["original_text"]
    policy_graphs = policy_graphs.replace('\n\n', '\n').split('\n')

    g_id = 0  # the index of a graph
    g_dic = {}

    topN = [] # store words with score top 5

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
            if len(preprocess_string(s)) == 0:
                continue

            s.replace("..", ".")
            w = 'January' if 'date' in column_name else column_name
            topN_tmp = w2v_sentence(w, s)
            topN = topN + topN_tmp
            topN = list(set(topN))
            topN.sort(reverse=True, key=lambda y: y[1])
            topN = topN[:TOP_N]
            score = topN_tmp[0][1]
            g_dic[g_id].append({"sentence_id": s_id, "sentence": s, "score": 0})
            s_id = s_id + 1
        g_id = g_id + 1
    return topN, g_dic

'''
1. Calculate answer by QA base on q['Question'] and sentence
2. Calculate cos of answer and q['clarification']
'''
def tmp2(column_name, policy_id, question, clarification):
    policy_original_text = CoronaNet.query.filter_by(policy_id=policy_id).first().__dict__
    policy_graphs = policy_original_text["original_text"]
    policy_graphs = policy_graphs.replace('\n\n', '\n').split('\n')

    g_id = 0  # the index of a graph
    g_dic = {}

    topN = [] # store words with score top 5

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
            if len(preprocess_string(s)) == 0:
                continue

            s.replace("..", ".")
            answer = signle_QA(question, s, model_name)
            if answer == '':
                continue
            # topN_tmp = w2v_sentence(answer, clarification)
            cos = cos_two_sentences(answer, clarification)
            topN.append([answer, cos])
            g_dic[g_id].append({"sentence_id": s_id, "sentence": s, "score": 0})
            s_id = s_id + 1
        g_id = g_id + 1
    # topN = list(set())
    topN.sort(reverse=True, key=lambda y: y[1])
    topN = topN[:TOP_N]

    return topN, g_dic


def signle_QA(question, context, model_name):
    from transformers import pipeline

    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
    QA_input = {
        'question': question,
        'context': context
    }
    res = nlp(QA_input)

    return res['answer']


def get_annotation_progress(pid, q_objs):
    policy = CoronaNet.query.filter_by(policy_id=pid).first()
    for q in q_objs:
        obj_property = getValue(policy, q["columnName"])
        qid = q["id"]

        if q["taskType"] == 0 or q["taskType"] == 1 or q["taskType"] == 2:
            if obj_property is None or obj_property == "":
                annotation_progress[pid][qid] = False
            else:
                annotation_progress[pid][qid] = True
    a = 0
    b = len(annotation_progress[pid])
    for k in annotation_progress[pid]:
        if annotation_progress[pid][k]:
            a = a + 1

    return a, b


def get_policy_by_prolific_id(prolific_id):
    policy = CoronaNet.query.filter_by(prolific_id=prolific_id).first()

    if policy is None:
        res = CoronaNet.query.order_by(desc(CoronaNet.policy_id)).first()

        if res is None:
            pid_tmp = 1
        else:
            pid_tmp = res.policy_id + 1

        policy = CoronaNet(policy_id=pid_tmp, prolific_id=prolific_id, status=1, original_text=original_text,
                           loading_time=0)
        db.session.add(policy)
        db.session.commit()

        policy = CoronaNet.query.filter_by(prolific_id=prolific_id).first()

    return policy