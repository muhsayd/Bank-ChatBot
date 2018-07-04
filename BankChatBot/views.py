from flask import render_template, request, jsonify, redirect, url_for

from datetime import datetime
from BankChatBot import app

import random
import spacy

nlp = spacy.load('en')

CheckingAccount = [{ 'Description': 'Opening Balance',               'Date': '01/01/2018', 'Debit': 0.0,   'Credit': 0.0,   'Balance': 8000.0 },
                   { 'Description': 'Salary Deposit',                'Date': '02/01/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 14000.0 },
                   { 'Description': 'Home Rent',                     'Date': '03/01/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 12000.0 },
                   { 'Description': 'Market Purchasing',             'Date': '04/01/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 11000.0 },
                   { 'Description': 'Car Parking',                   'Date': '05/01/2018', 'Debit': 200.0, 'Credit': 0.0,   'Balance': 10800.0 },
                   { 'Description': 'Hospital and Medicine',         'Date': '10/01/2018', 'Debit': 80.0,  'Credit': 0.0,   'Balance': 10720.0 },
                   { 'Description': 'Coffee and food from Starbucks','Date': '14/01/2018', 'Debit': 90.50, 'Credit': 0.0,   'Balance': 10629.50 },
                   { 'Description': 'Gas expenses',                  'Date': '20/01/2018', 'Debit': 600.80,'Credit': 0.0,   'Balance': 10028.70 },
                   { 'Description': 'Water expenses',                'Date': '20/01/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 9908.70 },
                   { 'Description': 'Electricity expenses',          'Date': '20/01/2018', 'Debit': 800.50,'Credit': 0.0,   'Balance': 9108.20 },
                   { 'Description': 'Internet expenses',             'Date': '20/01/2018', 'Debit': 150.45,'Credit': 0.0,   'Balance': 8957.75 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '26/01/2018', 'Debit': 1300.0,'Credit': 0.0,   'Balance': 7657.75 },
                   { 'Description': 'Salary Deposit',                'Date': '01/02/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 13657.75 },
                   { 'Description': 'Home Rent',                     'Date': '02/02/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 11657.75 },
                   { 'Description': 'Super market purchasing',       'Date': '02/02/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 10657.75 },
                   { 'Description': 'Fixing Car issues',             'Date': '01/02/2018', 'Debit': 550.0, 'Credit': 0.0,   'Balance': 10107.75 },
                   { 'Description': 'Food and drinks from park',     'Date': '04/02/2018', 'Debit': 90.0,  'Credit': 0.0,   'Balance': 10017.75 },
                   { 'Description': 'Gas expenses',                  'Date': '09/02/2018', 'Debit': 600.0, 'Credit': 0.0,   'Balance': 9417.75 },
                   { 'Description': 'Water expenses',                'Date': '11/02/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 9297.75 },
                   { 'Description': 'Electricity expenses',          'Date': '18/02/2018', 'Debit': 800.0, 'Credit': 0.0,   'Balance': 8497.75 },
                   { 'Description': 'Internet expenses',             'Date': '23/02/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 8347.75 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '27/02/2018', 'Debit': 1300.0,'Credit': 0.0,   'Balance': 7047.75 },
                   { 'Description': 'Salary Deposit',                'Date': '01/03/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 13047.75 },
                   { 'Description': 'Home Rent',                     'Date': '01/03/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 11047.75 },
                   { 'Description': 'Super market purchasing',       'Date': '01/03/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 10047.75 },
                   { 'Description': 'Food and drinks from park',     'Date': '01/03/2018', 'Debit': 237.38,'Credit': 0.0,   'Balance': 9810.37 },
                   { 'Description': 'Gas expenses',                  'Date': '09/03/2018', 'Debit': 600.0, 'Credit': 0.0,   'Balance': 9210.37 },
                   { 'Description': 'Water expenses',                'Date': '11/03/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 9090.37 },
                   { 'Description': 'Electricity expenses',          'Date': '18/03/2018', 'Debit': 800.0, 'Credit': 0.0,   'Balance': 8290.37 },
                   { 'Description': 'Internet expenses',             'Date': '23/03/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 8140.37 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '27/03/2018', 'Debit': 1300.0,'Credit': 0.0,   'Balance': 6840.37 },
                   { 'Description': 'Salary Deposit',                'Date': '01/04/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 12840.37 },
                   { 'Description': 'Home Rent',                     'Date': '05/04/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 10840.37 },
                   { 'Description': 'Super market purchasing',       'Date': '08/04/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 9840.37 },
                   { 'Description': 'Foods from shopping mall',      'Date': '13/04/2018', 'Debit': 122.20,'Credit': 0.0,   'Balance': 9718.17 },
                   { 'Description': 'Gas expenses',                  'Date': '18/04/2018', 'Debit': 402.0, 'Credit': 0.0,   'Balance': 9316.17 },
                   { 'Description': 'Electricity expenses',          'Date': '20/04/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 9166.17 },
                   { 'Description': 'Internet expenses',             'Date': '24/04/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 9046.17 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '30/04/2018', 'Debit': 1300.0,'Credit': 0.0,   'Balance': 7746.17 }]

SavingsAccount = [{ 'Description': 'Opening Balance',                'Date': '01/01/2018', 'Debit': 0.0,   'Credit': 0.0,   'Balance': 19000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '05/01/2018', 'Debit': 0.0,   'Credit': 3000.0,'Balance': 22000.0 },
                  { 'Description': 'Transfer to Checking Account',   'Date': '13/01/2018', 'Debit': 4000.0,'Credit': 0.0,   'Balance': 18000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '26/01/2018', 'Debit': 0.0,   'Credit': 1500.0,'Balance': 19500.0 },
                  { 'Description': 'Transfer to Checking Account',   'Date': '12/02/2018', 'Debit': 2500.0,'Credit': 0.0,   'Balance': 17000.0 },
                  { 'Description': 'Transfer to Checking Account',   'Date': '02/02/2018', 'Debit': 4000.0,'Credit': 0.0,   'Balance': 13000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '05/03/2018', 'Debit': 0.0,   'Credit': 1000.0,'Balance': 14000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '22/03/2018', 'Debit': 0.0,   'Credit': 2000.0,'Balance': 16000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '28/03/2018', 'Debit': 0.0,   'Credit': 3000.0,'Balance': 19000.0 },
                  { 'Description': 'Transfer to Checking Account',   'Date': '04/04/2018', 'Debit': 4000.0,'Credit': 0.0,   'Balance': 15000.0 },
                  { 'Description': 'Transfer from Checking Account', 'Date': '21/04/2018', 'Debit': 0.0,   'Credit': 3000.0,'Balance': 18000.0 }]
questions_list = []
answers_list = []
similarity_threshold = 0.6

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html',
        title='Home Page',
        year=datetime.now().year)

@app.route('/statement')
def statement():
    return render_template('statement.html',
        title='Account Statement',
        CheckingAccount=CheckingAccount,
        SavingsAccount=SavingsAccount,
        year=datetime.now().year)

@app.route('/process_question', methods=['POST'])
def process_question():
    question = request.args.get('question')
    questions_list.append(question)
    answer = ''
    chart_type = ''
    expected_questions = ''

    hi_intent = ['hi', 'hello']
    how_are_you_intent = ['how are you','how are you ?', 'hi, how are you ?', 'hello, how are you ?']
    thanks_intent = ['thank', 'thanks', 'thank you', 'many thanks', 'Thank you so much', 'thankful', 'grateful']
    welcome_intent = ['welcome', 'glade to see you', "what's up"]
    balance_intent = ['check how much money do i have', 'show available money on my checking account', 'how much money is available on my bank account',
                      'balance', 'my balance', 'check my account', "what's the balance in my savings account", 'show balance', 'check my savings account']
    bad_question = ["I didn't get that. Can you say it again?", "Sorry, can you tell me again?", "Sorry, can you say that again?", 
                    "I'm afraid I don't understand."]

    # Very long question => bad question
    if len(question) > 70:
        answer = bad_question[random.randint(0, len(bad_question) - 1)]
    elif get_similarity(hi_intent, question) >= similarity_threshold:
        hello = ['Hi, how can I help you ?', 'Hello, Welcome to BankBot by Stallion.ai.', 'How can I help you ?', 'Hello, and thanks for choosing BankBot by Stallion.ai.']
        answer = hello[random.randint(0, len(hello) - 1)]
    elif get_similarity(how_are_you_intent, question) >= similarity_threshold:
        how_are_you = ['Doing great, thanks.', 'I am fine thank you', 'How can I help you ?', 'Feeling wonderful!']
        answer = how_are_you[random.randint(0, len(how_are_you) - 1)]
    elif get_similarity(welcome_intent, question) >= similarity_threshold:
        welcome = ['Welcome to BankBot by Stallion.ai.', 'Welcome and thanks for choosing BankBot by Stallion.ai.', 'How can I help you ?']
        answer = welcome[random.randint(0, len(welcome) - 1)]
    elif get_similarity(thanks_intent, question) >= similarity_threshold:
        thanks = ['You are Welcome!', 'Thanks.', "Anytime. That's what I'm here for.", "It's my pleasure to help.", "My pleasure."]
        answer = thanks[random.randint(0, len(thanks) - 1)]
    elif get_similarity(balance_intent, question) >= similarity_threshold:
        answer = 'Your balance is 123 Dirhams'
    elif question.find('bar') >= 0:
        chart_type = 'bar'
    elif question.find('pie') >= 0:
        chart_type = 'pie'
    elif question.find('donut') >= 0:
        chart_type = 'donut'
    else:
        answer = bad_question[random.randint(0, len(bad_question) - 1)]

    answers_list.append(answer)
    data=[{ 'name': 'Jan', 'count': 400 }, { 'name': 'Feb', 'count': 5876 }, { 'name': 'Mar', 'count': 745 }, { 'name': 'Apr', 'count': 6098 }]
    chart_title='Chart Title'
    tooltip='Tooltip'

    return jsonify(question=question,
                   unique_id=str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second),
                   data=data,
                   chart_title=chart_title,
                   tooltip=tooltip,
                   chart_type=chart_type,
                   answer=answer)
    
# Get maximum similarity from list items
def get_similarity(intent, question):
    similarity = []
    qust = nlp(question)
    for i in intent:
        doc = nlp(i)
        similarity.append(qust.similarity(doc))

    similarity = sorted(similarity, reverse=True)
    return similarity[0]
