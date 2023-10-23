from flask import Flask, render_template, request, jsonify
import pymongo
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics
from jaeger_client import Config
import logging
from os import getenv
from flask_cors import CORS

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "example-mongodb"
app.config["MONGO_URI"] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)

metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info('app_info', 'App info', version='1.0')
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

by_endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Count request by request endpoint',
    labels={'endpoint': lambda: request.endpoint}
)
JAEGER_AGENT_HOST = getenv('JAEGER_AGENT_HOST', 'localhost')
CORS(app)

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
            'local_agent': {'reporting_host': JAEGER_AGENT_HOST},
        },
        service_name=service,
    )
    return config.initialize_tracer()

tracer = init_tracer('backend')

class InvalidHandle(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        error_message = dict(self.payload or ())
        error_message['message'] = self.message
        return error_message


@app.errorhandler(InvalidHandle)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/error')
@by_endpoint_counter
def err():
    return 'Error Server', 500


@app.route('/')
@by_endpoint_counter
def homepage(): 
    with tracer.start_span('hello-world'):
        return "Hello World"


@app.route("/api")
@by_endpoint_counter
def my_api():
    with tracer.start_span('api'):
        answer = "My custom API => ..."
    return jsonify(repsonse=answer)


@app.route("/star", methods=["POST"])
@by_endpoint_counter
def add_star():
    with tracer.start_span('star'):
        try:
            star = mongo.db.stars
            name = request.json["name"]
            distance = request.json["distance"]
            star_id = star.insert({"name": name, "distance": distance})
            new_star = star.find_one({"_id": star_id})
            output = {"name": new_star["name"], "distance": new_star["distance"]}
        except Exception as e:
            app.logger.info("The error is: ", e)
    return jsonify({"result": output})

@app.route('/4xx')
@by_endpoint_counter
def get_error():
    raise InvalidHandle('error 4xx appear', status_code=410)

@app.route('/health-check')
@by_endpoint_counter
def healthcheck():
    app.logger.info('Helth check successfull')
    return jsonify({"result": "OK - healthy"})


if __name__ == "__main__":
    app.run(threaded=True)
