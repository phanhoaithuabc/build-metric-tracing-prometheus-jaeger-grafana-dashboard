## Verify the monitoring installation

*TODO:* run `kubectl` command to show the running pods and services for all components. Take a screenshot of the output and include it here to verify the installation
```bash
kubectl get pod,svc -n monitoring
kubectl get pod,svc -n observability
```
<img src="answer-img/monitoring-pod-svc.png"></img>

## Setup the Jaeger and Prometheus source
*TODO:* Expose Grafana to the internet and then setup Prometheus as a data source. Provide a screenshot of the home page after logging into Grafana.
```bash
kubectl port-forward -n monitoring service/prometheus-kube-prometheus-prometheus 9090:9090
kubectl port-forward -n monitoring prometheus-grafana-8c58b6b68-cpzp9  3000:3000
# get pass word grafana of admin
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```
<img src="answer-img/grafana-after-log-in.png"></img>

## Create a Basic Dashboard
*TODO:* Create a dashboard in Grafana that shows Prometheus as a source. Take a screenshot and include it here.
<img src="answer-img/grafana-dashboard.png"></img>

## Describe SLO/SLI
*TODO:* Describe, in your own words, what the SLIs are, based on an SLO of *monthly uptime* and *request response time*.

A Service-Level Indicator (SLI) is a metric that is used to follow the Service Level Objective (SLO) define.
The SLO in this case is based on *monthly uptime* and *request response time*, so the SLI is the value of the uptime and the response times:
- Monthly uptime: For example, an SLO of 99.9% monthly uptime means that the service should be available 99.9% of the time in a month. SLI would be the actual measurement of the uptime and maybe we would achieved 99% uptime or 98% uptime.
- Request response time: For example, an SLO of 100 milliseconds request response time means that the service should respond to requests in 100 milliseconds or less.

## Creating SLI metrics.
*TODO:* It is important to know why we want to measure certain metrics for our customer. Describe in detail 5 metrics to measure these SLIs. 

- SLO: latency               SLI: response time of requests
- SLO: failure rate          SLI: the amount of failures in a unit of time
- SLO: uptime                SLI: time a service is alive
- SLO: network capcity       SLI: average bandwidth in a specifi period of time
- SLO: resource capcity      SLI: the amount of CPU and RAM usage

## Create a Dashboard to measure our SLIs
*TODO:* Create a dashboard to measure the uptime of the frontend and backend services We will also want to measure to measure 40x and 50x errors. Create a dashboard that show these values over a 24 hour period and take a screenshot.
<img src="answer-img/grafana-uptime-error.png"></img>

## Tracing our Flask App
*TODO:*  We will create a Jaeger span to measure the processes on the backend. Once you fill in the span, provide a screenshot of it here. Also provide a (screenshot) sample Python file containing a trace and span code used to perform Jaeger traces on the backend service.

<img align='center' src="answer-img/tracer-backend-api.png"></img>

> A (screenshot) sample Python file containing a trace and span code used to perform Jaeger traces on the backend service [app.py](./reference-app/backend/app.py)

<img src="answer-img/tracer-code.png"></img>

## Jaeger in Dashboards
*TODO:* Now that the trace is running, let's add the metric to our current Grafana dashboard. Once this is completed, provide a screenshot of it here.
```bash
# add URL datasource into grafana
ingress_name=$(kubectl get -n ${namespace} ingress -o jsonpath='{.items[0].metadata.name}'); \
ingress_port=$(kubectl get -n ${namespace} ingress -o jsonpath='{.items[0].spec.defaultBackend.service.port.number}'); \
echo -e "\n\n${ingress_name}.${namespace}.svc.cluster.local:${ingress_port}"

# => simplest-query.observability.svc.cluster.local:16686
```
<img src="answer-img/tracer-dashboard-backend.png"></img>

## Report Error
*TODO:* Using the template below, write a trouble ticket for the developers, to explain the errors that you are seeing (400, 500, latency) and to let them know the file that is causing the issue also include a screenshot of the tracer span to demonstrate how we can user a tracer to locate errors easily.

TROUBLE TICKET:

- Name: Endpoint **/star** fail (405 Method Not Allowed)
- Date: 20 Oct 2023, 15:09:40
- Subject: Failure on **/star** endpoint, problem on MongoDB
- Affected Area: Backend Service (./reference-app/backend/app.py on code)
- Severity: Critical
- Description: **mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb** we define in code does - not exist in the cluster. We need to creare one for backend.

## Creating SLIs and SLOs
*TODO:* We want to create an SLO guaranteeing that our application has a 99.95% uptime per month. Name four SLIs that you would use to measure the success of this SLO.
- For Saturation: Memory consumption and CPU percentages in last 1 month
- For Error Check: Infrastructure uptime percentages in last 1 month
- For Latency Check: Request/response time percentages less then 300 ms
- For Trafic Check: The average number of requests/minute in the last 24 hours

## Building KPIs for our plan
*TODO*: Now that we have our SLIs and SLOs, create a list of 2-3 KPIs to accurately measure these metrics as well as a description of why those KPIs were chosen. We will make a dashboard for this, but first write them down here.
- Latency: Response time less than 300 milliseconds.
- Failure rate: Errors per second less then 1%, success response rate per second > 99%.
- Uptime: No interruptions when container is running.
- Network capcity: Successful request per second > 98%
- Resource capcity: CPU usage, Memory usage per pod 98% available.

## Final Dashboard
*TODO*: Create a Dashboard containing graphs that capture all the metrics of your KPIs and adequately representing your SLIs and SLOs. Include a screenshot of the dashboard here, and write a text description of what graphs are represented in the dashboard.  

<img src="answer-img/Final-Dashboard.png"></img>

- Jaeger Trace Backend: Display duration of backend api
- CPU Usages ALL: The CPU usage of ALL the Flask applicatin
- Memory usages: The Memory usage of ALL the Flask applicatin
- Uptime: Uptime of each service
- 4XX, 5XX Responses: 4XX HTTP, 5XX error code
- Average Request/min : Number of successful Flask requests per minute (response code=200).