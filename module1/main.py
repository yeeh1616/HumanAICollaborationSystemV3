from flask import Blueprint, render_template
from module1.annotation import get_selection_AI, get_annotation_progress, get_completation_AI, get_selection_manual, \
    get_completation_manual, get_completation_AI_cache
from module1.dao import upate_loading_time
from module1.global_variable import annotation_progress, q_cache
from module1.helper import get_policy_by_prolific_id, get_max_task_num, read_json_file_to_object, \
    write_object_to_json_file, get_ai_or_human, get_completed_task_num
from module1.models import CoronaNet

import time
import json

from module1.summary import get_summary_AI

bp_main = Blueprint('main', __name__)


@bp_main.route("/main/<string:prolific_id>", methods=['GET', 'POST'])
@bp_main.route("/main/<string:prolific_id>/<int:question_id>", methods=['GET', 'POST'])
def get_summary(prolific_id, question_id=1):
    tic = time.perf_counter()
    policy = get_policy_by_prolific_id(prolific_id)
    policy_id = policy.policy_id

    ai_or_human = get_ai_or_human()
    max_task_num = get_max_task_num()
    completed_task_num = get_completed_task_num()

    if completed_task_num >= max_task_num:
        return "Policy {} is not found.".format(policy_id)

    q, q_objs = get_question(policy_id, question_id)

    res = "Error: unknown task type."

    if ai_or_human == '1':
        if q["taskType"] == 0:
            policy = CoronaNet.query.filter_by(policy_id=policy_id).first()

            policy.highlighted_text = policy.original_text.split('\n')

            if policy.description is None:
                policy.description = ''

            complete, total = get_annotation_progress(policy_id, q_objs)
            res = render_template('summary_manual.html',
                                    policy=policy,
                                    annotation_progress=annotation_progress[policy_id],
                                    complete=complete,
                                    total=total,
                                    pre=question_id - 1,
                                    next=question_id + 1)
        else:
            if q["taskType"] == 1:
                return get_selection_manual(policy_id, question_id)
            elif q["taskType"] == 2:
                return get_completation_manual(policy_id, question_id)
    else:
        if q["taskType"] == 0:
            policy, has_summary = get_summary_AI(policy_id)
            complete, total = get_annotation_progress(policy_id, q_objs)
            res = render_template('summary.html',
                                    policy=policy,
                                    has_summary=has_summary,
                                    annotation_progress=annotation_progress[policy_id],
                                    complete=complete,
                                    total=total,
                                    pre=question_id - 1,
                                    next=question_id + 1)
        else:
            if q["taskType"] == 1:
                policy, summary_list, graph_list = get_selection_AI(policy_id, question_id, q)

                if policy_id % 2 == 0:
                    from module1.helper_tmp import set_selection_AI_tmp
                    set_selection_AI_tmp(q)
            elif q["taskType"] == 2:
                policy, summary_list, graph_list = get_completation_AI_cache(policy_id, question_id, q)

                if summary_list is None or graph_list is None:
                    policy, summary_list, graph_list = get_completation_AI(policy_id, question_id, q)
                    write_object_to_json_file('ai_t2_cache_q_answers', q['answers'])
                    write_object_to_json_file('ai_t2_cache_summary_list', summary_list)
                    write_object_to_json_file('ai_t2_cache_graph_list', graph_list)

                if policy_id % 2 == 0:
                  from module1.helper_tmp import set_completation_AI_tmp
                  set_completation_AI_tmp(q)

            complete, total = get_annotation_progress(policy_id, q_objs)
            res = render_template('annotation.html',
                                   policy=policy,
                                   q=q,
                                   summary_list=summary_list,
                                   graph_list=graph_list,
                                   annotation_progress=annotation_progress[policy_id],
                                   complete=complete,
                                   total=total,
                                   pre=question_id - 1,
                                   next=question_id + 1)
        toc = time.perf_counter()
        upate_loading_time(policy_id, int(toc - tic))
    return res


def get_question(policy_id, question_id):
    if policy_id not in q_cache.keys():
        with open('./module1/static/questions.json', encoding="utf8") as f:
            q_objs = json.load(f)
            q_cache[policy_id] = q_objs
        annotation_progress[policy_id] = {}
    else:
        q_objs = q_cache[policy_id]

    for q in q_objs:
        if q['id'] == question_id:
            return q, q_objs
    return None, None