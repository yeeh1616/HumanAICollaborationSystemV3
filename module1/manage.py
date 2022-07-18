import json

from flask import Blueprint, render_template, redirect, url_for, request

import module1.global_variable
from module1 import db
from module1.models import CoronaNet, Conf

bp_manage = Blueprint('manage', __name__)


@bp_manage.route("/manage", methods=['GET', 'POST'])
def manage():
    status = None
    try:
        status = request.args["status"]
    except:
        pass

    if status is None:
        policies = CoronaNet.query.filter_by(status=1).all()
    else:
        policies = CoronaNet.query.all()
    ai_or_human = Conf.query.filter_by(key="ai_or_human").first()
    max_task_num = Conf.query.filter_by(key="max_task_num").first()
    return render_template('manage.html', policies=policies,
                           max_task_num=max_task_num.value,
                           ai_or_human=ai_or_human.value)


@bp_manage.route("/updatepid", methods=['POST'])
def update_pid():
    try:
        conf = Conf.query.filter_by(key="max_task_num").first()
        conf.value = request.form.get("pid")
        db.session.commit()
    except:
        pass
    return redirect(url_for('manage.manage'))


@bp_manage.route("/clearall", methods=['GET', 'POST'])
def clearall():
    flag = True

    try:
        num_rows_deleted = db.session.query(CoronaNet).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flag = False

    return redirect(url_for('manage.manage'))


@bp_manage.route("/clearall0", methods=['GET', 'POST'])
def clearall0():
    flag = True

    try:
        num_rows_deleted = db.session.query(CoronaNet).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flag = False

    return json.dumps({'success': flag}), 200, {'ContentType': 'application/json'}


@bp_manage.route("/ai_or_human", methods=['GET', 'POST'])
def ai_or_human():
    try:
        conf = Conf.query.filter_by(key="ai_or_human").first()
        conf.value = request.form.get("ai_or_human")
        db.session.commit()
    except:
        pass
    return redirect(url_for('manage.manage'))