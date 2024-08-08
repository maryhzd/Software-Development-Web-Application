from flask import Flask, render_template, request, redirect, url_for
from models import db, Todo
from forms import TodoForm
from sqlalchemy import case

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Todo(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('index'))
    
    # Corrected case usage
    todos = Todo.query.order_by(
        case(
            (Todo.priority == 'High', 1),
            (Todo.priority == 'Medium', 2),
            (Todo.priority == 'Low', 3)
        )
    ).all()
    
    return render_template('index.html', form=form, todos=todos)


@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
def update(todo_id):
    todo = Todo.query.get(todo_id)
    form = TodoForm(obj=todo)
    if form.validate_on_submit():
        todo.title = form.title.data
        todo.description = form.description.data
        todo.priority = form.priority.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', form=form, todo=todo)

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
