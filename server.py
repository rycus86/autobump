import math
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from endpoints import check_auth_header
from endpoints.goland import update_goland
from endpoints.pycharm import update_pycharm
from endpoints.idea import update_intellij_idea


app = Flask(__name__)
PrometheusMetrics(app, buckets=[float(n + 1) for n in range(30)] + [math.inf])

app.before_request(check_auth_header)
app.add_url_rule('/update/goland/<owner>/<name>', 'update_goland', update_goland, methods=['POST'])
app.add_url_rule('/update/pycharm/<owner>/<name>', 'update_pycharm', update_pycharm, methods=['POST'])
app.add_url_rule('/update/idea/<owner>/<name>', 'update_intellij_idea', update_intellij_idea, methods=['POST'])


if __name__ == '__main__':
    app.run('0.0.0.0', 5000, threaded=True)
