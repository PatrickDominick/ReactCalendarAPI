from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_cors import CORS 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://hfovdpxcyjckwm:39b14e8b4699c2378d1d8fee3f591595e0a22c4abd1df83e0c4f3dc427596793@ec2-44-197-40-76.compute-1.amazonaws.com:5432/df9kdreg14tc4t"

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    start_day = db.Column(db.Integer, nullable = False)
    days_in_month = db.Column(db.Integer, nullable = False)
    days_in_previous_month = db.Column(db.Integer, nullable = False)

    def __init__(self, name, year, start_day, days_in_month, days_in_previous_month) :
        self.name = name
        self.year = year
        self.start_day = start_day
        self.days_in_month = days_in_month
        self.days_in_previous_month = days_in_previous_month

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable = False)
    date = db.Column(db.Integer, nullable = False)
    month_id = db.Column(db.Integer, nullable = False)

    def __init__(self, text, date, month_id):
        self.text = text
        self.date = date
        self.month_id = month_id


class MonthSchema(ma.Schema):
    class Meta: 
        fields = ("id", "name", "year", "start_day", "days_in_month", "days_in_previous_month")

month_schema = MonthSchema()
multiple_month_schema = MonthSchema(many = True)

class ReminderSchema(ma.Schema):
    class Meta: 
        fields = ("id", "text", "date", "month_id")

reminder_schema = ReminderSchema()
multiple_reminder_schema = ReminderSchema(many=True)


@app.route("/month/add", methods=["POST"])
def add_month():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON fool!")

    post_data = request.get_json()
    name = post_data.get("name")
    year = post_data.get("year")
    start_day = post_data.get("start_day")
    days_in_month = post_data.get("days_in_month")
    days_in_previous_month = post_data.get("days_in_previous_month")

    existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
    if existing_month_check is not None: 
        return jsonify("Error: Month already exists fool!")

    new_record = Month(name, year, start_day, days_in_month, days_in_previous_month)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(month_schema.dump(new_record))

@app.route("/month/add/multiple", methods=["POST"])
def add_multiple_months():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON fool!")

    post_data = request.get_json()
    data = post_data.get("data")

    new_records = []

    for month in data: 
        name = month.get("name")
        year = month.get("year")
        start_day = month.get("start_day")
        days_in_month = month.get("days_in_month")
        days_in_previous_month = month.get("days_in_previous_month")

        existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
        if existing_month_check is None:
        
            new_record = Month(name, year, start_day, days_in_month, days_in_previous_month)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

    return jsonify(multiple_month_schema.dump(new_records))


@app.route ("/month/get", methods=["GET"])
def get_months():
    all_months = db.session.query(Month).all()
    return jsonify(multiple_month_schema.dump(all_months))

@app.route("/reminder/add", methods=["POST"])
def add_reminder():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON fool!")

    post_data = request.get_json()
    text = post_data.get("text")
    date = post_data.get("date")
    month_id = post_data.get("month_id")
    
    existing_reminder_check = db.session.query(Reminder).filter(Reminder.date == date).filter(Reminder.month_id == month_id).first()
    if existing_reminder_check is not None: 
        return jsonify("Error: Reminder already exists fool!")

    new_record = Reminder(text, date, month_id)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(reminder_schema.dump(new_record))


@app.route("/reminder/get<month_id>/<date>", methods=["GET"])
def get_reminder(month_id, date): 
    reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    return jsonify(reminder_schema.dump(reminder))

@app.route ("/reminder/get", methods=["GET"])
def get_reminders():
    all_reminders = db.session.query(Reminder).all()
    return jsonify(multiple_reminder_schema.dump(all_reminders))

@app.route ("/reminder/get/week/<month_id>/<dates>", methods=["GET"])
def get_reminders_by_week(month_id, dates):
    all_reminders = []
    for date in dates.split("-"):
        reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
        all_reminders.append(reminder)
    return jsonify(multiple_reminder_schema.dump(all_reminders))

@app.route ("/reminder/update/<month_id>/<date>", methods = ["PUT"])
def update_reminder(month_id, date):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON fool!")

    put_data = request.get_json()
    text = put_data.get("text")

    reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()

    reminder.text = text
    db.session.commit()

    return jsonify(reminder_schema.dump(reminder))

@app.route("/reminder/delete/<month_id>/<date>", methods = ["DELETE"])
def delete_reminder(month_id, date):
    reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    db.session.delete(reminder)
    db.session.commit()
    return jsonify(reminder_schema.dump(reminder))

if __name__ == "__main__":
    app.run(debug=True)