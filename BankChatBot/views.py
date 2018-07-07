# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify, redirect, url_for

from datetime import datetime
from dateutil import parser

from BankChatBot import app
from BankChatBot import intents

import os
import json
import operator
import re
import random
import csv
    

# Reading Checking Account from external csv
CheckingAccount = []
with open('CheckingAccount.csv') as f:
    CheckingAccount = [{k: str(v) if k == u'Description' or k == u'Date' else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]


# Reading Savings Account from external csv
SavingsAccount = []
with open('SavingsAccount.csv') as f:
    SavingsAccount = [{k: str(v) if k == u'Description' or k == u'Date' else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

DefaultCurrency = u'Dirhams'
DefaultRate = 1.0

CurrencyRates = [{ u'name': u'Dirhams', u'name_ar': u'درهم', u'value': 1.0 },
                 { u'name': u'Dollars', u'name_ar': u'دولار', u'value': 0.27 },
                 { u'name': u'Euro', u'name_ar': u'يورو', u'value': 0.23 }]

Months = [u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August', u'September', u'October', u'November', u'December']
questions_list = []
answers_list = []
similarity_threshold = 0.6

@app.route('/')
@app.route('/home')
def home():
    with open('bag_of_intents.json', 'r') as f:
        intents.bag_of_intents = json.load(f)

    #f = open('bag_of_intents.json', 'r')
    #intents.bag_of_intents = json.load(f)
    #keys = f.read()
    #print(str(keys))
    #keys = keys.decode('utf-8')
    #intents.bag_of_intents = json.loads(keys)
    #f.close()

    #if os.path.isfile('bag_of_intents.json'):
    #    os.remove('bag_of_intents.json')

    #f = open('bag_of_intents.json','w')
    #json.dump(intents.bag_of_intents, f, ensure_ascii=False)
    #f.close()

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
    question.encode("utf-8")

    answer = ''
    chart_type = ''
    expected_questions = ''
    data = []
    chart_title = ''
    tooltip = ''

    bad_question = [u"I didn't get that. Can you say it again?", u"Sorry, can you tell me again?", u"Sorry, can you say that again?", 
                    u"I'm afraid I don't understand."]
    bad_question_ar = [u'عفواً, لم أفهم سيادتكم', u'آسف هل يمكنك السؤال مرة أخرى', u'لم أفهم السؤال سيدي', u'أخشى أني لم أفهم حضرتكم']

    # Very long question or not English one => bad question
    if len(question) > 70:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer, similarity='')

    # print dynamic answer
    similarity = intents.get_all_similarity(question)
    if similarity[0]['value'] < similarity_threshold:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer, similarity=similarity)

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
    if question.lower().find(u'dollar') >= 0 or question.find(u'دولار') >= 0:
        DefaultCurrency = u'Dollars' if not intents.is_arabic(question) else u'دولار'
    elif question.lower().find(u'euro') >= 0 or question.find(u'يورو') >= 0:
        DefaultCurrency = u'Euro' if not intents.is_arabic(question) else u'يورو'
    elif question.lower().find(u'dirham') >= 0 or question.find(u'درهم') >= 0:
        DefaultCurrency = u'Dirhams' if not intents.is_arabic(question) else u'درهم'

    for cur in CurrencyRates:
        if DefaultCurrency == cur['name'] or DefaultCurrency == cur['name_ar']:
            DefaultRate = cur['value']

    if intents.is_arabic(question) and DefaultCurrency == u'Dirhams':
        DefaultCurrency = u'درهم'
    elif not intents.is_arabic(question) and DefaultCurrency == u'درهم':
        DefaultCurrency = u'Dirhams'

    if intents.is_arabic(question) and DefaultCurrency == u'Dollars':
        DefaultCurrency = u'دولار'
    elif not intents.is_arabic(question) and DefaultCurrency == u'دولار':
        DefaultCurrency = u'Dollars'

    if intents.is_arabic(question) and DefaultCurrency == u'Euro':
        DefaultCurrency = u'يورو'
    elif not intents.is_arabic(question) and DefaultCurrency == u'يورو':
        DefaultCurrency = u'Euro'

    # print Checking Account
    if similarity[0]['intent'] == u'balance_checking_account':
        answer += str(round(CheckingAccount[len(CheckingAccount) - 1]['Balance'] * DefaultRate, 2)) + ' ' + DefaultCurrency
    
    # print Savings Account
    if similarity[0]['intent'] == u'balance_savings_account':
        answer += str(round(SavingsAccount[len(SavingsAccount) - 1]['Balance'] * DefaultRate, 2)) + ' ' + DefaultCurrency

    # print expenses
    if similarity[0]['intent'] == u'expenses':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find(u'expense') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = u'Total Expenses'
        tooltip = DefaultCurrency
        if question.find(u'bar') >= 0:
            chart_type = u'bar'
        elif question.find(u'pie') >= 0:
            chart_type = u'pie'
        elif question.find(u'donut') >= 0:
            chart_type = u'donut'

    # print loans
    if similarity[0]['intent'] == u'loans':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].find(u'loans') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = u'Total Loans'
        tooltip = DefaultCurrency
        if question.find(u'bar') >= 0:
            chart_type = u'bar'
        elif question.find(u'pie') >= 0:
            chart_type = u'pie'
        elif question.find(u'donut') >= 0:
            chart_type = u'donut'

    # print car
    if similarity[0]['intent'] == u'car':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find(u'car') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = u'Car Expenditure'
        tooltip = DefaultCurrency
        if question.find(u'bar') >= 0:
            chart_type = u'bar'
        elif question.find(u'pie') >= 0:
            chart_type = u'pie'
        elif question.find(u'donut') >= 0:
            chart_type = u'donut'

    # print food
    if similarity[0]['intent'] == u'food':
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat['Date'], dayfirst=True).month != startmonth:
                data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat['Date'], dayfirst=True).month
                monthly = 0.0

            if stat['Description'].lower().find(u'food') >= 0:
                total += stat['Debit']
                monthly += stat['Debit']

        data.append({'name': Months[startmonth - 1], 'count': round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + ' ' + DefaultCurrency

        chart_title = u'Food Expenditure'
        tooltip = DefaultCurrency
        if question.find(u'bar') >= 0:
            chart_type = u'bar'
        elif question.find(u'pie') >= 0:
            chart_type = u'pie'
        elif question.find(u'donut') >= 0:
            chart_type = u'donut'
            
    questions_list.append(question)
    answers_list.append(answer)

    return jsonify(question=question,
                   unique_id=str(datetime.now().year) + '_' + str(datetime.now().month) + '_' + str(datetime.now().day) + '_' + str(datetime.now().hour) + '_' + str(datetime.now().minute) + '_' + str(datetime.now().second),
                   data=data,
                   chart_title=chart_title,
                   tooltip=tooltip,
                   chart_type=chart_type,
                   answer=answer,
                   similarity=similarity)
    
