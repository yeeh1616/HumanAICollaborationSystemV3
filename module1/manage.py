from flask import Blueprint, render_template

from module1 import db
from module1.models import CoronaNet

import json

bp_manage = Blueprint('manage', __name__)


@bp_manage.route("/manage", methods=['GET', 'POST'])
def manage():
    return render_template('manage.html')


@bp_manage.route("/clearall", methods=['GET', 'POST'])
def clearall():
    flag = True

    try:
        num_rows_deleted = db.session.query(CoronaNet).delete()
        db.session.commit()
    except:
        db.session.rollback()
        flag = False

    return json.dumps({'success': flag}), 200, {'ContentType': 'application/json'}
