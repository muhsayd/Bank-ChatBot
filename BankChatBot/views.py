from flask import render_template, request, jsonify, redirect, url_for

from datetime import datetime
from dateutil import parser

from BankChatBot import app
from BankChatBot import intents

import random
import csv
    

# Reading Checking Account from external csv
CheckingAccount = []
with open('CheckingAccount.csv') as f:
    CheckingAccount = [{k: str(v) if k == 'Description' or k == 'Date' else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]


# Reading Savings Account from external csv
SavingsAccount = []
with open('SavingsAccount.csv') as f:
    SavingsAccount = [{k: str(v) if k == 'Description' or k == 'Date' else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

DefaultCurrency = 'Dirhams'
DefaultRate = 1.0

CurrencyRates = [{ 'name': 'Dirhams', 'name_ar': 'درهم', 'value': 1.0 },
                 { 'name': 'Dollars', 'name_ar': 'دولار', 'value': 0.27 },
                 { 'name': 'Euro', 'name_ar': 'يورو', 'value': 0.23 }]

Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
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
    
    answer = ''
    chart_type = ''
    expected_questions = ''
    data = []
    chart_title = ''
    tooltip = ''

    bad_question = ["I didn't get that. Can you say it again?", "Sorry, can you tell me again?", "Sorry, can you say that again?", 
                    "I'm afraid I don't understand."]
    bad_question_ar = ['عفواً, لم أفهم سيادتكم', 'آسف هل يمكنك السؤال مرة أخرى', 'لم أفهم السؤال سيدي', 'أخشى أني لم أفهم حضرتكم']

    # Very long question or not English one => bad question
    if len(question) > 70:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer)

    # print dynamic answer
    similarity = intents.get_all_similarity(question)
    if similarity[0]['value'] < similarity_threshold:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer)

    for intt in intents.bag_of_intents:
        if intt['intent'] == similarity[0]['intent']:
            if not intents.is_arabic(question):
                answer = intt['answers'][random.randint(0, len(intt['answers']) - 1)]
            else:
                answer = intt['answers_ar'][random.randint(0, len(intt['answers_ar']) - 1)]
            break
    
    global DefaultCurrency
    global DefaultRate

    # Change Default Currency
    if question.lower().find('dollar') >= 0 or question.find('دولار') >= 0:
        DefaultCurrency = 'Dollars' if not intents.is_arabic(question) else 'دولار'
    elif question.lower().find('euro') >= 0 or question.find('يورو') >= 0:
        DefaultCurrency = 'Euro' if not intents.is_arabic(question) else 'يورو'
    elif question.lower().find('dirham') >= 0 or question.find('درهم') >= 0:
        DefaultCurrency = 'Dirhams' if not intents.is_arabic(question) else 'درهم'

    for cur in CurrencyRates:
        if DefaultCurrency == cur['name'] or DefaultCurrency == cur['name_ar']:
            DefaultRate = cur['value']

    if intents.is_arabic(question) and DefaultCurrency == 'Dirhams':
        DefaultCurrency = 'درهم'
    elif not intents.is_arabic(question) and DefaultCurrency == 'درهم':
        DefaultCurrency = 'Dirhams'

    if intents.is_arabic(question) and DefaultCurrency == 'Dollars':
        DefaultCurrency = 'دولار'
    elif not intents.is_arabic(question) and DefaultCurrency == 'دولار':
        DefaultCurrency = 'Dollars'

    if intents.is_arabic(question) and DefaultCurrency == 'Euro':
        DefaultCurrency = 'يورو'
    elif not intents.is_arabic(question) and DefaultCurrency == 'يورو':
        DefaultCurrency = 'Euro'

    # print Checking Account
    if similarity[0]['intent'] == 'balance_checking_account':
        answer += str(round(CheckingAccount[len(CheckingAccount) - 1]['Balance'] * DefaultRate, 2)) + ' ' + DefaultCurrency
    
    # print Savings Account
    if similarity[0]['intent'] == 'balance_savings_account':
        answer += str(round(SavingsAccount[len(SavingsAccount) - 1]['Balance'] * DefaultRate, 2)) + ' ' + DefaultCurrency

    # print expenses
    if similarity[0]['intent'] == 'expenses':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find('expense') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = 'Total Expenses'
        tooltip = DefaultCurrency
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    # print loans
    if similarity[0]['intent'] == 'loans':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find('loans') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = 'Total Loans'
        tooltip = DefaultCurrency
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    # print car
    if similarity[0]['intent'] == 'car':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find('car') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = 'Car Expenditure'
        tooltip = DefaultCurrency
        if question.find('bar') >= 0:
            chart_type = 'bar'
        elif question.find('pie') >= 0:
            chart_type = 'pie'
        elif question.find('donut') >= 0:
            chart_type = 'donut'

    # print food
    if similarity[0]['intent'] == 'food':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find('food') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = 'Food Expenditure'
        tooltip = DefaultCurrency
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
    
