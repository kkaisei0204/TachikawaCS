from flask_sqlalchemy import SQLAlchemy

# データベースのインスタンスを独立させることで、app.pyとmodels.pyの循環参照を防ぎます
db = SQLAlchemy()