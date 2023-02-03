import os
import json
import time
import uuid

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


class ServiceQueue:

    def __init__(self):
        self.normal_queue = []
        self.priority_queue = []
        self.missed_queue = []
        self.status = "active"

    def isNormalEmpty(self) -> bool:
        return True if len(self.normal_queue) == 0 else False

    def isPriorityEmpty(self) -> bool:
        return True if len(self.priority_queue) == 0 else False

    def front(self):
        if not self.isPriorityEmpty():
            return self.priority_queue[0]['queue_number']
        elif not self.isNormalEmpty():
            return self.normal_queue[0]['queue_number']
        else:
            return None

    def next(self):
        if not self.isPriorityEmpty():
            return self.priority_queue.pop(0)
        elif not self.isNormalEmpty():
            return self.normal_queue.pop(0)
        else:
            return None

    def hold(self):
        if not self.isPriorityEmpty():
            self.missed_queue.append(self.priority_queue.pop(0))
        elif not self.isNormalEmpty():
            self.missed_queue.append(self.normal_queue.pop(0))
        else:
            return None

    def enqueue(self, new_patient):
        self.normal_queue.append(new_patient.__dict__)


class Patient:
    def __init__(self):
        self.patient_id = get_short_id()
        self.queue_number = None

    def getQueueNumber(self, queue, prefix="A"):
        if not queue:
            return prefix + '001'
        last_queue_number = queue[-1]['queue_number']
        last_3_digits = int(last_queue_number[-3:])
        self.queue_number = prefix + str(last_3_digits + 1).zfill(3)


def read_queue():
    if os.path.exists("queue.txt"):
        with open("queue.txt", "r") as f:
            return json.load(f)
    else:
        return {
            "branch-1": {
                "consulting": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                },
                "examination": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                }
            },
            "branch-2": {
                "consulting": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                },
                "examination": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                }
            },
            "branch-3": {
                "consulting": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                },
                "examination": {
                    "normal_queue": [],
                    "priority_queue": [],
                    "missed_queue": [],
                    "status": "active"
                }
            }
        }


def write_queue(queue):
    with open("queue.txt", "w") as f:
        json.dump(queue, f)


def read_service_queue(queue, branch, service):
    s = ServiceQueue()
    current_q = queue[branch][service]
    s.normal_queue = current_q["normal_queue"]
    s.priority_queue = current_q["priority_queue"]
    s.missed_queue = current_q["missed_queue"]
    s.status = current_q["status"]
    return s


def write_service_queue(current_queue, queue, branch, service):
    queue[branch][service] = current_queue.__dict__


def get_short_id():
    array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
             "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
             "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
             ]
    id = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(id[start:end], 16)
        buffer.append(array[val % 62])
    return "".join(buffer)
##### Patient #####


@app.route("/patient/main", methods=["GET", "POST"])
def main():
    queue = read_queue()
    if request.method == "POST":
        branch = request.form.get("branch")
        service = request.form.get("service")
        current_queue = read_service_queue(queue, branch, service)
        prefix = "A" if service == "consulting" else "B"
        new_patient = Patient()
        new_patient.getQueueNumber(current_queue.normal_queue, prefix)
        current_queue.enqueue(new_patient)
        write_service_queue(current_queue, queue, branch, service)
        write_queue(queue)
        return redirect(url_for("patient", branch=branch, service=service, patient_id=new_patient.patient_id))
    return render_template("patient_main.html", queue=queue)


@app.route("/patient/<branch>/<service>/<patient_id>")
def patient(branch, service, patient_id):
    queue = read_queue()
    current_queue = read_service_queue(queue, branch, service)
    queue_number = "Not Found"
    for p in current_queue.normal_queue:
        if p['patient_id'] == patient_id:
            queue_number= p['queue_number']
    if queue_number == "Not Found":
        for p in current_queue.priority_queue:
            if p['patient_id'] == patient_id:
                queue_number = p['queue_number']
    return render_template("patient_status.html", branch=branch, service=service, queue_number=queue_number)


##### Counter #####
@app.route('/<branch>/<counter>/<service>/queue', methods=['GET', 'POST'])
def queue_system(branch, service, counter):
    queue = read_queue()
    current_queue = read_service_queue(queue, branch, service)
    current_calling = current_queue.front()

    if request.method == 'POST':
        if request.form['action'] == "Next":
            print("Next")
            current_queue.next()
            write_service_queue(current_queue, queue, branch, service)

        elif request.form['action'] == 'Hold':
            print("Next")
            current_queue.hold()
            write_service_queue(current_queue, queue, branch, service)

        elif request.form['action'] == 'Re-schedule':
            pass
        elif request.form['action'] == 'Set priority':
            pass

    write_queue(queue)
    # current = queue[branch][service]['normal_queue']
    return render_template('counter_main.html', branch_name=branch, service=service, counter_name=counter, current_calling=current_calling)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
