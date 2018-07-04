from flask import render_template, request, jsonify, redirect, url_for

from datetime import datetime
from dateutil import parser
from BankChatBot import app
from langdetect import detect

import random
import spacy
import operator

nlp = spacy.load('en')

CheckingAccount = [{ 'Description': 'Opening Balance',               'Date': '01/01/2018', 'Debit': 0.0,   'Credit': 0.0,   'Balance': 8000.0 },
                   { 'Description': 'Salary Deposit',                'Date': '02/01/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 14000.0 },
                   { 'Description': 'Home Rent',                     'Date': '03/01/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 12000.0 },
                   { 'Description': 'Market Purchasing',             'Date': '04/01/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 11000.0 },
                   { 'Description': 'Car Parking',                   'Date': '05/01/2018', 'Debit': 200.0, 'Credit': 0.0,   'Balance': 10800.0 },
                   { 'Description': 'Hospital and Medicine',         'Date': '10/01/2018', 'Debit': 80.0,  'Credit': 0.0,   'Balance': 10720.0 },
                   { 'Description': 'Coffee and food from Starbucks','Date': '14/01/2018', 'Debit': 90.5,  'Credit': 0.0,   'Balance': 10629.5 },
                   { 'Description': 'Gas expenses',                  'Date': '20/01/2018', 'Debit': 321.8, 'Credit': 0.0,   'Balance': 10307.7 },
                   { 'Description': 'Water expenses',                'Date': '20/01/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 10187.7 },
                   { 'Description': 'Electricity expenses',          'Date': '20/01/2018', 'Debit': 309.5, 'Credit': 0.0,   'Balance': 9878.2 },
                   { 'Description': 'Internet expenses',             'Date': '20/01/2018', 'Debit': 150.45,'Credit': 0.0,   'Balance': 9727.75 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '26/01/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 8727.75 },
                   { 'Description': 'Salary Deposit',                'Date': '01/02/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 14727.75 },
                   { 'Description': 'Home Rent',                     'Date': '02/02/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 12727.75 },
                   { 'Description': 'Super market purchasing',       'Date': '02/02/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 11727.75 },
                   { 'Description': 'Fixing Car issues',             'Date': '01/02/2018', 'Debit': 550.0, 'Credit': 0.0,   'Balance': 11177.75 },
                   { 'Description': 'Food and drinks from park',     'Date': '04/02/2018', 'Debit': 90.0,  'Credit': 0.0,   'Balance': 11087.75 },
                   { 'Description': 'Gas expenses',                  'Date': '09/02/2018', 'Debit': 340.0, 'Credit': 0.0,   'Balance': 10747.75 },
                   { 'Description': 'Water expenses',                'Date': '11/02/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 10627.75 },
                   { 'Description': 'Electricity expenses',          'Date': '18/02/2018', 'Debit': 60.0,  'Credit': 0.0,   'Balance': 10567.75 },
                   { 'Description': 'Internet expenses',             'Date': '23/02/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 10417.75 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '27/02/2018', 'Debit': 1100.0,'Credit': 0.0,   'Balance': 9317.75 },
                   { 'Description': 'Salary Deposit',                'Date': '01/03/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 15317.75 },
                   { 'Description': 'Home Rent',                     'Date': '01/03/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 13317.75 },
                   { 'Description': 'Super market purchasing',       'Date': '01/03/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 12317.75 },
                   { 'Description': 'Food and drinks from park',     'Date': '01/03/2018', 'Debit': 237.38,'Credit': 0.0,   'Balance': 12080.37 },
                   { 'Description': 'Gas expenses',                  'Date': '09/03/2018', 'Debit': 600.0, 'Credit': 0.0,   'Balance': 11480.37 },
                   { 'Description': 'Water expenses',                'Date': '11/03/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 11360.37 },
                   { 'Description': 'Electricity expenses',          'Date': '18/03/2018', 'Debit': 800.0, 'Credit': 0.0,   'Balance': 10560.37 },
                   { 'Description': 'Internet expenses',             'Date': '23/03/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 10410.37 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '27/03/2018', 'Debit': 1300.0,'Credit': 0.0,   'Balance': 9110.37 },
                   { 'Description': 'Salary Deposit',                'Date': '01/04/2018', 'Debit': 0.0,   'Credit': 6000.0,'Balance': 15110.37 },
                   { 'Description': 'Home Rent',                     'Date': '05/04/2018', 'Debit': 2000.0,'Credit': 0.0,   'Balance': 13110.37 },
                   { 'Description': 'Super market purchasing',       'Date': '08/04/2018', 'Debit': 1000.0,'Credit': 0.0,   'Balance': 12110.37 },
                   { 'Description': 'Foods from shopping mall',      'Date': '13/04/2018', 'Debit': 122.2, 'Credit': 0.0,   'Balance': 11988.17 },
                   { 'Description': 'Gas expenses',                  'Date': '18/04/2018', 'Debit': 402.0, 'Credit': 0.0,   'Balance': 11586.17 },
                   { 'Description': 'Electricity expenses',          'Date': '20/04/2018', 'Debit': 150.0, 'Credit': 0.0,   'Balance': 11436.17 },
                   { 'Description': 'Internet expenses',             'Date': '24/04/2018', 'Debit': 120.0, 'Credit': 0.0,   'Balance': 11316.17 },
                   { 'Description': 'loans and advances to Hydel',   'Date': '30/04/2018', 'Debit': 900.0, 'Credit': 0.0,   'Balance': 10416.17 },
                   { 'Description': 'Car Fuel',                      'Date': '30/04/2018', 'Debit': 416.17,'Credit': 0.0,   'Balance': 10000.0 }]

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

Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
questions_list = []
answers_list = []
similarity_threshold = 0.6

bag_of_intents = [{
                      'intent': 'hi', 
                      'values': ['hi', 'hello'],
                      'answers': ['Hi, how can I help you ?', 'Hello, Welcome to BankBot by Stallion.ai.', 'How can I help you ?', 
                                  'Hello, and thanks for choosing BankBot by Stallion.ai.']
                  },
                  {
                      'intent': 'how_are_you',
                      'values': ['how are you','how are you ?', 'hi, how are you ?', 'hello, how are you ?'],
                      'answers': ['Doing great, thanks.', 'I am fine thank you', 'How can I help you ?', 'Feeling wonderful!']
                  },
                  {
                      'intent': 'thanks',
                      'values': ['thank', 'thanks', 'thank you', 'many thanks', 'Thank you so much', 'thankful', 'grateful'],
                      'answers': ['You are Welcome!', 'Thanks.', "Anytime. That's what I'm here for.", "It's my pleasure to help.", "My pleasure."]
                  },
                  {
                      'intent': 'welcome',
                      'values': ['welcome', 'glade to see you', "what's up"],
                      'answers': ['Welcome to BankBot by Stallion.ai.', 'Welcome and thanks for choosing BankBot by Stallion.ai.', 'How can I help you ?']
                  },
                  {
                      'intent': 'balance_checking_account',
                      'values': ['check how much money do i have', 'show available money on my checking account',
                                 'show available money on my checking', 'how much money is available at my bank account', 'balance', 'my balance', 'check my account', 
                                 "what's the balance in my checking account", "what's the balance on my checking", 'show balance', 'check my checking account', 'check my checking'],
                      'keywords': ['checking', 'checking account'],
                      'answers': ['your balance in Checking Account is: ']
                  },
                  {
                      'intent': 'balance_savings_account',
                      'values': ['check how much money do i have in my savings account', 'check how much money do i have on my savings', 
                                 'show available money in my savings account', 'show available money at my savings', 
                                 'how much money is available on my savings account', 'how much money is available on my savings', 'my savings account balance',
                                 'savings balance', 'check my balance on savings account', 'check my balance on savings', 
                                 "what's the balance in my savings account", "what's the balance in my savings", 'show balance in savings', 
                                 'check my savings account'],
                      'keywords': ['savings', 'savings account'],
                      'answers': ['your balance in Savings Account is: ']
                   },
                   {
                      'intent': 'expenses',
                      'values': ['how much money i spent', 'show my expenses', 'my expenses', "what's my expenses", 'show expenses', 'check my expenses'],
                      'keywords': ['expense', 'expenses'],
                      'answers': ['your total expenses is: ']
                   },
                   {
                      'intent': 'loans',
                      'values': ['how much loans', 'show my loans', 'my loans', "what's my loans", 'show loans', 'check my loans'],
                      'keywords': ['loan', 'loans'],
                      'answers': ['your total loans is: ']
                   },
                   {
                      'intent': 'car',
                      'values': ['how much car expenditure', 'show my car', 'my car spend', "what's my car expenditure", 'show car', 'check my car expenditure'],
                      'keywords': ['car', 'cars'],
                      'answers': ['your car expenditure is: ']
                   },
                   {
                      'intent': 'food',
                      'values': ['how much food expenditure', 'show my food', 'my food spend', "what's my food expenditure", 'show food', 'check my food expenditure'],
                      'keywords': ['food', 'foods'],
                      'answers': ['your food expenditure is: ']
                   }]


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
    
    answer = ''
    chart_type = ''
    expected_questions = ''
    data = []
    chart_title = ''
    tooltip = ''

    bad_question = ["I didn't get that. Can you say it again?", "Sorry, can you tell me again?", "Sorry, can you say that again?", 
                    "I'm afraid I don't understand."]

    # Very long question or not English one => bad question
    if len(question) > 70:
        answer = bad_question[random.randint(0, len(bad_question) - 1)]
        return jsonify(question=question, answer=answer)

    similarity = get_all_similarity(question)
    if similarity[0]['value'] < similarity_threshold:
        answer = bad_question[random.randint(0, len(bad_question) - 1)]
        return jsonify(question=question, answer=answer)

    for intt in bag_of_intents:
        if intt['intent'] == similarity[0]['intent']:
            answer = intt['answers'][random.randint(0, len(intt['answers']) - 1)]
            break
    
    if similarity[0]['intent'] == 'balance_checking_account':
        answer += str(CheckingAccount[len(CheckingAccount) - 1]['Balance'])
    
    if similarity[0]['intent'] == 'balance_savings_account':
        answer += str(SavingsAccount[len(SavingsAccount) - 1]['Balance'])

    if similarity[0]['intent'] == 'expenses':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': monthly})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find('expense') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': monthly})
        answer += str(total)

        chart_title = 'Total Expenses'
        tooltip = 'Dirhams'
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    if similarity[0]['intent'] == 'loans':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': monthly})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find('loans') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': monthly})
        answer += str(total)

        chart_title = 'Total Loans'
        tooltip = 'Dirhams'
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    if similarity[0]['intent'] == 'car':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': monthly})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find('car') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': monthly})
        answer += str(total)

        chart_title = 'Car Expenditure'
        tooltip = 'Dirhams'
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    if similarity[0]['intent'] == 'food':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': monthly})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find('food') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': monthly})
        answer += str(total)

        chart_title = 'Food Expenditure'
        tooltip = 'Dirhams'
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'
            
    questions_list.append(question)
    answers_list.append(answer)

    return jsonify(question=question,
                   unique_id=str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second),
                   data=data,
                   chart_title=chart_title,
                   tooltip=tooltip,
                   chart_type=chart_type,
                   answer=answer)
    
# Get maximum similarity from list items
#def get_intent_similarity(intent, question):
#    similarity = []
#    qust = nlp(question)

#    for i in intent:
#        doc = nlp(i)
#        similarity.append(qust.similarity(doc))

#    similarity = sorted(similarity, reverse=True)
#    return similarity[0]

def get_all_similarity(question):
    results = []
    similarity = []

    qust = nlp(question)
    
    for intent in bag_of_intents:
        similarity = []
        for i in intent['values']:
            doc = nlp(i)
            similarity.append(qust.similarity(doc))
            
        # explicit keyword mention means more weight to the intent
        if 'keywords' in intent:
            for i in intent['keywords']:
                if question.find(i) >= 0:
                    similarity = [s * 1.3 for s in similarity]
                    break

        # if question is not english decrease weights of similarity
        if detect(question) != 'en':
            similarity = [s * 0.7 for s in similarity]

        similarity = sorted(similarity, reverse=True)
        results.append({ 'intent': intent['intent'], 'value': (similarity[0] + similarity[1]) / 2 })

    results = sorted(results, key=operator.itemgetter('value'), reverse=True)
    return results

