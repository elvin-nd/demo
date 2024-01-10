from flask import Flask
from methods import Tasks

app = Flask(__name__)
tasks = Tasks()


@app.route("/", methods=["GET"])
def get_tasks():
    return tasks.get_all_tasks()

@app.route("/active", methods=["GET"])
def get_active():
    return tasks.get_all_running_tasks()

@app.route("/", methods=["POST"])
def create_task():
    return tasks.create_task()


@app.route("/toggle/<task_id>", methods=["PUT"])
def toggle_task(task_id):
    return tasks.toggle_active(task_id)


@app.route("/update/<task_id>", methods=["PUT"])
def update_task(task_id):
    return tasks.update_task(task_id)

@app.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    return tasks.delete_task(task_id)




if __name__ in "__main__":
    app.run(debug=True)
