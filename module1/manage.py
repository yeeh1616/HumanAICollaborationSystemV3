from flask import Blueprint, render_template, redirect, url_for

from module1 import db
from module1.models import CoronaNet

import json

bp_manage = Blueprint('manage', __name__)


@bp_manage.route("/manage", methods=['GET', 'POST'])
def manage():
    policies = CoronaNet.query.all()
    return render_template('manage.html', policies=policies)


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
