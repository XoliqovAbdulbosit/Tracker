from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

DATABASE_URL = 'sqlite:///main.db'
Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Integer)
    description = Column(String)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    title = Column(String)
    description = Column(String)


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@app.route('/finances', methods=['GET', 'POST'])
def finances():
    session = Session()
    if request.method == 'POST':
        date = request.form['date']
        amount = request.form['amount']
        description = request.form['description']
        date = datetime.strptime(date, '%Y-%m-%d')
        transaction = Transaction(date=date, amount=int(amount), description=description)
        session.add(transaction)
        session.commit()
    transactions = session.query(Transaction).order_by(Transaction.date.desc()).all()
    data = {}
    daily = {}
    for transaction in transactions:
        if data.get(transaction.date, None) is None:
            data[transaction.date] = []
            daily[transaction.date] = 0
        data[transaction.date].append([transaction.amount, transaction.description])
        daily[transaction.date] += transaction.amount
    session.close()
    return render_template('finances.html', data=data, daily=daily)


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    session = Session()
    if request.method == 'POST':
        date = request.form['date']
        title = request.form['title']
        description = request.form['description']
        date = datetime.strptime(date, '%Y-%m-%d')
        task = Task(date=date, title=title, description=description)
        session.add(task)
        session.commit()
    tasks = session.query(Task).order_by(Task.date.desc()).all()
    session.close()
    return render_template('tasks.html', tasks=tasks)


@app.route('/tasks/delete/<int:id>', methods=['POST'])
def delete_tasks(id):
    session = Session()
    if request.method == 'POST':
        task = session.query(Task).get(id)
        session.delete(task)
        session.commit()
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run()
