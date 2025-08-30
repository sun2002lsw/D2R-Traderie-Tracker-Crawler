from flask import Flask, jsonify
import app


# 단순히 cloud run 에서 실행하기 위해 8080 포트 listen
flask_app = Flask(__name__)
flask_app.run(host="0.0.0.0", port=8080, debug=False)

# 실제 크롤링 서비스
app.run()
