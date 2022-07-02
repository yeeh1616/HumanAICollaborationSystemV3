from flask import Blueprint, render_template
from flask_login import login_required
from module1.models import CoronaNet

bp_annotation = Blueprint('view', __name__)


@bp_annotation.route("/policies", methods=['GET', 'POST'])
@login_required
def view():
    policy_list = CoronaNet.query.paginate(page=1, per_page=10)

    return render_template('policy_list.html', policy_list=policy_list)
