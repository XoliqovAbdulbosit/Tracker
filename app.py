from datetime import datetime
from flask import Flask, render_template, request
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


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


@app.route('/', methods=['GET', 'POST'])
def main():
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
    return render_template('home.html', data=data, daily=daily)


if __name__ == '__main__':
    app.run()
