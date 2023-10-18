from flask import Flask, render_template, request
import threading
import requests
import random
import time
from prometheus_flask_exporter import PrometheusMetrics
import logging
from jaeger_client import Config

app = Flask(__name__)
metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info('app_info', 'Application info', version='1.0')
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)
by_endpoint_counter = metrics.counter(
    'by_endpoint_counter', 'Request count by request endpoint',
    labels={'endpoint': lambda: request.endpoint}
)
endpoints = ('error', '4xx', 'health-check')

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
        },
        service_name=service,
    )
    return config.initialize_tracer()

tracer = init_tracer('frontend')


def random_endpoint():
    while True:
        try:
            target = random.choice(endpoints)
            backend_service = os.environ.get('BACKEND_ENDPOINT', default="https://localhost:8081")
            app.logger.info(backend_service)
            url_endpoint= f'{backend_service}/'+"%s" %target
            backend_response = requests.get(url_endpoint, timeout=1)
        except:
            pass


@app.route('/')
@by_endpoint_counter
def homepage():
    with tracer.start_span('random_endpoint') as span:
        threading.Thread(target=random_endpoint).start()
        for _ in range(4):
            thread = threading.Thread(target=random_endpoint)
            thread.daemon = True
            thread.start()
        while True:
            time.sleep(1)
    return render_template("main.html")
    

@app.route('/health-check')
@by_endpoint_counter
def healthcheck():
    app.logger.info('Helth check successfull')
    return jsonify({"result": "OK - healthy"})


if __name__ == "__main__":    
    app.run()