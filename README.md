# Hospital-Queuing-System

## Brief Description of the System

Hospitals and clinics may require such a queuing solution at their respective department such as registration, consultations, treatment, and pharmacy. Our system is a queueing system designed for hospitals with multiple branches. It has three main users, patients who need to queue for consulting or examination, counters who manage the order of the queue and CRO who controls the status of the queue.

## Installation

1. A source editor that can run a `.py` file
2. Install flask

## Usage

Open the following URL in browsers：

### For patients:

http://127.0.0.1:8080/patient/main

### For counter:

http://127.0.0.1:8000/{branch}/{counter}/{service_type}/queue

Please change the branch number, counter number and service type before entering the page

Each computer in the hospital will have a pre-set URL, for example, http://127.0.0.1:8000/branch-1/counter1/consulting/queue. Employees can use the existing webpage without changing the route name.

### For CRO:

http://127.0.0.1:8080/CRO/main

## Contributing

Contributions are welcome. Please submit a pull request with your changes and email us.
