import nltk
import gensim.downloader as api

from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from sentence_transformers import SentenceTransformer
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
from transformers import pipeline
from nltk.corpus import stopwords
from flask_bcrypt import Bcrypt
from nltk import download
from flask import Flask

db = SQLAlchemy()
bcrypt = Bcrypt()

download('stopwords')
stop_words = stopwords.words('english')
wv = api.load('word2vec-google-news-300')
model_name = 'deepset/bert-base-cased-squad2'
tokenizer = AutoTokenizer.from_pretrained("deepset/bert-base-cased-squad2")
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
model2 = SentenceTransformer('bert-base-nli-mean-tokens')
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
nltk.download('stopwords')
nltk.download('punkt')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'thisisasecretkey'

    db.init_app(app)
    bcrypt.init_app(app)

    from .main import bp_main as main_blueprint
    app.register_blueprint(main_blueprint)

    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # login_manager.login_view = 'auth.login'
    #
    # from .models import User
    #
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(int(user_id))
    #
    # from .auth import bp_auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)
    #
    # from .policies import bp_policies as policies_blueprint
    # app.register_blueprint(policies_blueprint)
    #
    from .summary import bp_summary as summary_blueprint
    app.register_blueprint(summary_blueprint)

    from .annotation import bp_annotation as annotation_blueprint
    app.register_blueprint(annotation_blueprint)

    from .configuration import bp_configuration as configuration_blueprint
    app.register_blueprint(configuration_blueprint)

    from .manage import bp_manage as manage_blueprint
    app.register_blueprint(manage_blueprint)

    return app
