from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# configuration for connecting to postgres db
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2:///project_tracker"
app.config["SECRET_KEY"] = b'\x95@\x93\x16G\x13\xa0\x1bKwe,\xef#\xcdr\xde\xe7\xaf\xd1}\xd10M'
db = SQLAlchemy(app)


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=50))
    task = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")




class Task(db.Model):
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    description = db.Column(db.String(length=50))
    project = db.relationship("Project", back_populates="task")


# Define route
@app.route("/")
def show_projects():
    return render_template("index.html", projects=Project.query.all())


@app.route("/project/<project_id>")
def show_tasks(project_id):
    return render_template("project-tasks.html",
                           project=Project.query.filter_by(project_id=project_id).first(),
                           tasks=Task.query.filter_by(project_id=project_id).all())


@app.route("/add/project", methods=['POST'])
def add_project():
    if not request.form['project-title']:
        flash("Enter a title for your new project","red")
    else:
        project = Project(title=request.form['project-title'])
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully","green")
    return redirect(url_for('show_projects'))



@app.route("/add/task/<project_id>", methods=['POST'])
def add_task(project_id):
    if not request.form['task-name']:
        flash("Enter a description for your new task", "red")
    else:
        task = Task(description=request.form['task-name'],project_id=project_id)
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully","green")
    return redirect(url_for('show_tasks', project_id=project_id))

@app.route("/delete/project/<project_id>", methods=['POST'])
def delete_project(project_id):
    project = Project.query.filter_by(project_id=project_id).first()
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('show_projects'))

@app.route("/delete/task/<task_id>", methods=['POST'])
def delete_task(task_id):
    pending_delete_task = Task.query.filter_by(task_id=task_id).first()
    original_project_id = pending_delete_task.project.project_id


    db.session.delete(pending_delete_task)
    db.session.commit()
    return redirect(url_for('show_tasks',project_id=original_project_id))


app.run(debug=True, host='127.0.0.1', port=3000)
