from module1 import db
from module1.models import CoronaNet


def upate_loading_time(policy_id, loading_time):
    corona_net = CoronaNet.query.filter_by(policy_id=policy_id).first()
    corona_net.loading_time = corona_net.loading_time + loading_time
    db.session.commit()