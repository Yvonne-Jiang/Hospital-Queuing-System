import json
import os
import uuid

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


class ServiceQueue:

    def __init__(self):
        self.normal_queue = []
        self.priority_queue = []
        self.missed_queue = []
        self.status = "active"

    def queue(self):
        return self.priority_queue + self.normal_queue

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

    def nextThree(self):
        lq = len(self.queue())
        if lq > 0:
            return [p['queue_number'] for p in self.queue()[1:4]]
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

    def enqueue(self, new_patient, priority_type):
        if priority_type == "normal_queue":
            self.normal_queue.append(new_patient)
        else:
            self.priority_queue.append(new_patient)

    def searchByQnum(self, q_number):
        # Search the patient by queue number.
        patient = None
        for patient_dict in self.queue():
            if patient_dict['queue_number'] == q_number:
                patient = patient_dict
        return patient

    def searchByID(self, p_id):
        # Search the patient by patient_id.
        # For patient status
        patient = None
        for patient_dict in self.queue():
            if patient_dict['patient_id'] == p_id:
                patient = patient_dict
        return patient

    def searchMiss(self, q_number, delete=False):
        # Search the patient by queue number.
        # For re-schedule
        patient = None
        for patient_dict in self.missed_queue:
            if patient_dict['queue_number'] == q_number:
                patient = patient_dict
        if delete and patient != None:
            self.missed_queue.remove(patient)
        return patient

    def reschedule(self, q_number):
        # Delete in missed queue and insert into normal queue
        patient_dict = self.searchMiss(q_number, True)
        self.normal_queue.insert(2, patient_dict)

    def stopQueue(self):
        self.status = "inactive"

    def reInitiateQueue(self):
        self.status = "active"


def read_queue():
    if os.path.exists("queue.txt"):
        with open("queue.txt", "r") as f:
            return json.load(f)
    else:
        print("create queue")
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


def getQueueNumber(queue, prefix="A"):
    if not queue:
        return prefix + '001'
    idx = []
    for p in queue:
        if p['queue_number'][0] == prefix:
            idx.append(int(p['queue_number'][-3:]))
    return prefix + str(max(idx) + 1).zfill(3)


def write_service_queue(current_queue, queue, branch, service):
    queue[branch][service] = current_queue.__dict__


def get_short_id():
    array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
             "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
             "v", "w", "x", "y", "z",
             "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
             "V", "W", "X", "Y", "Z"
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
    if request.method == 'POST':
        branch, service = request.form.get("branch_service").split("_")
        current_queue = read_service_queue(queue, branch, service)
        prefix = "A" if service == "consulting" else "B"
        priority_type = request.form["priority_type"]
        if priority_type == "priority_queue":
            prefix = prefix.lower()
        new_patient = {'patient_id': get_short_id(), 'queue_number': getQueueNumber(
            eval("current_queue." + priority_type), prefix)}
        current_queue.enqueue(new_patient, priority_type)
        write_service_queue(current_queue, queue, branch, service)
        write_queue(queue)
        return redirect(url_for("patient", branch=branch, service=service, patient_id=new_patient['patient_id']))
    return render_template("patient_main.html", queue=queue)


@app.route("/patient/<branch>/<service>/<patient_id>")
def patient(branch, service, patient_id):
    queue = read_queue()
    current_queue = read_service_queue(queue, branch, service)
    queue_number = current_queue.searchByID(patient_id)['queue_number']
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

        # elif request.form['action'] == 'Re-schedule':
        #     pass
        # elif request.form['action'] == 'Set priority':
        #     pass

    write_queue(queue)
    # current = queue[branch][service]['normal_queue']
    return render_template('counter_main.html', branch_name=branch, service=service, counter_name=counter,
                           current_calling=current_calling)


##### CRO #####

@app.route("/CRO/main", methods=['GET', 'POST'])
def cro_main():
    queue = read_queue()
    if request.method == 'POST':
        branch, service = request.form.get("branch_service").split("_")
        return redirect(url_for("cro_queue", branch=branch, service=service))
    return render_template("cro_main.html", queue=queue)


@app.route("/CRO/<branch>/<service>/queue", methods=['GET', 'POST'])
def cro_queue(branch, service):
    queue = read_queue()
    current_queue = read_service_queue(queue, branch, service)
    normal_num = len(current_queue.normal_queue)
    priority_num = len(current_queue.priority_queue)
    status = current_queue.status
    change_status = "Stop" if status == "active" else 'Re-initiate'

    if request.method == 'POST':
        if request.form['action'] == "Stop":
            current_queue.stopQueue()
            status = current_queue.status
            change_status = 'Re-initiate'
            write_service_queue(current_queue, queue, branch, service)
            write_queue(queue)

        elif request.form['action'] == 'Re-initiate':
            current_queue.reInitiateQueue()
            status = current_queue.status
            change_status = 'Stop'
            write_service_queue(current_queue, queue, branch, service)
            write_queue(queue)

        elif request.form['action'] == 'Re-schedule':
            return redirect(url_for("reschedule", branch=branch, service=service))
    return render_template('cro_queue.html', branch_name=branch, service=service, normal_num=normal_num,
                           priority_num=priority_num, status=status, change_status=change_status)


@app.route('/CRO/<branch>/<service>/queue/reschedule', methods=['GET', 'POST'])
def reschedule(branch, service):
    queue = read_queue()
    current_queue = read_service_queue(queue, branch, service)
    normal_num = len(current_queue.normal_queue)
    priority_num = len(current_queue.priority_queue)
    status = current_queue.status
    change_status = "Stop" if status == "active" else 'Re-initiate'
    missed_nums = [p['queue_number'] for p in current_queue.missed_queue]
    if request.method == 'POST':
        # Get the patient number to be re-scheduled
        patient_number = request.form.get('patient_number')
        current_queue.reschedule(patient_number)
        write_service_queue(current_queue, queue, branch, service)
        write_queue(queue)
        return redirect(url_for("cro_queue", branch=branch, service=service))

    return render_template('reschedule.html', branch_name=branch, service=service, normal_num=normal_num,
                           priority_num=priority_num, status=status, change_status=change_status)


@app.route("/<branch>/display", methods=['GET'])
def display(branch):
    queue = read_queue()
    consulting_queue = read_service_queue(queue, branch, "consulting")
    examination_queue = read_service_queue(queue, branch, "examination")
    con_now_serving = consulting_queue.front()
    ex_now_serving = examination_queue.front()
    con_next_serving = consulting_queue.nextThree()
    ex_next_serving = examination_queue.nextThree()
    return render_template('display.html', branch=branch, con_now_serving=con_now_serving,
                           ex_now_serving=ex_now_serving, con_next_serving=con_next_serving,
                           ex_next_serving=ex_next_serving)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
