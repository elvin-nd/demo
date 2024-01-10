from db import db
import datetime as dt
from flask import request
from bson import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler


class Tasks:
    def __init__(self):
        self.schedule = BackgroundScheduler()
        self.db = db.get_db()
        self.log = db.get_log()
        self.active_tasks = {}
        self._run_initial()
        self.schedule.start()

    def _create_schedule(self, time, activity):
        task = ""
        print(time, activity, "--------------")

        match activity:
            case "delete_record":
                activity = self.delete_record
            case "delete_something":
                activity = self.delete_something
            case "some_other_task":
                activity = self.some_other_tasks

        task = self.schedule.add_job(activity, "interval", **time)
        # Add more cases as needed
        return task

    def _run_initial(self):
        query = self.db.find({"active": True})
        for row in query:
            task = self._create_schedule(row["time"], row["activity"])
            task_id = str(row["_id"])
            self.active_tasks[task_id] = task

    # sample tasks
    def delete_record(self):
        self.log.insert_one({"name": 'delete_record'})

    def delete_something(self):
        self.log.insert_one({"name": 'delete_something'})

    def some_other_tasks(self):
        self.log.insert_one({"name": 'do_something_else'})

    # sample tasks

    def get_all_running_tasks(self):
        return str(self.active_tasks)

    def get_all_tasks(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$activity",  # Field to group by
                    "tasks": {"$push": "$$ROOT"},  # Include all documents in each group
                }
            },
            {
                "$project": {
                    "_id": 1,  # Include the grouped field (_id)
                    "tasks": 1,  # Include the array of documents for each group
                }
            },
        ]

        query = list(self.db.aggregate(pipeline))
        for row in query:
            for task in row["tasks"]:
                task["_id"] = str(task["_id"])
        return query

    def create_task(self):
        data = request.json
        _id = ObjectId()
        task_id = str(_id)
        task = self._create_schedule(data["time"], data["activity"])
        self.active_tasks[task_id] = task

        try:
            self.db.insert_one(
                {
                    "_id": _id,
                    "name": data["name"],
                    "time": data["time"],
                    "activity": data["activity"],
                    "active": True,
                }
            )
        except:
            task.remove()
            del self.active_tasks[task_id]

        return "ok"

    def toggle_active(self, task_id):
        task_id = ObjectId(task_id)

        task = self.db.find_one({"_id": task_id})

        if task:
            new_active_status = not task["active"]

            self.db.update_one(
                {"_id": task_id}, {"$set": {"active": new_active_status}}
            )

            if new_active_status:
                # Task is active, add the job back
                task_schedule = self._create_schedule(task["time"], task["activity"])
                self.active_tasks[str(task_id)] = task_schedule
            else:
                # Task is inactive, remove the job
                if str(task_id) in self.active_tasks:
                    self.active_tasks[str(task_id)].remove()
                    del self.active_tasks[str(task_id)]

            return "ok"

        return "Task not found"

    def update_task(self, task_id):
        data = request.json
        task_id = ObjectId(task_id)

        existing_task = self.db.find_one({"_id": task_id})

        if existing_task:
            # Update the task with the provided data
            updated_data = {
                "name": data.get("name", existing_task.get("name")),
                "time": data.get("time", existing_task.get("time")),
            }

            # Update the task in the database
            self.db.update_one(
                {"_id": task_id},
                {"$set": updated_data},
            )

            # Update the active_tasks dictionary if needed
            if task_id in self.active_tasks:
                self.active_tasks[task_id].remove()
                del self.active_tasks[task_id]

                updated_task_schedule = self._create_schedule(updated_data["time"], updated_data["activity"])
                self.active_tasks[task_id] = updated_task_schedule

            return "ok"
        
        return "Task not found"

    def delete_task(self, task_id):
        task_id = ObjectId(task_id)

        existing_task = self.db.find_one({"_id": task_id})

        if existing_task:
            # Remove the task from the database
            self.db.delete_one({"_id": task_id})

            # Remove the task from the active_tasks dictionary if it's there
            if task_id in self.active_tasks:
                self.active_tasks[task_id].remove()
                del self.active_tasks[task_id]

            return "ok"
        else:
            return "Task not found"