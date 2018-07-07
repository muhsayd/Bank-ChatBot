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
with open("CheckingAccount.csv") as f:
    CheckingAccount = [{k: str(v) if k == u"Description" or k == u"Date" else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]


# Reading Savings Account from external csv
SavingsAccount = []
with open("SavingsAccount.csv") as f:
    SavingsAccount = [{k: str(v) if k == u"Description" or k == u"Date" else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

DefaultCurrency = u"Dirhams"
DefaultRate = 1.0

CurrencyRates = [{ u"name": u"Dirhams", u"name_ar": u"درهم", u"value": 1.0 },
                 { u"name": u"Dollars", u"name_ar": u"دولار", u"value": 0.27 },
                 { u"name": u"Euro", u"name_ar": u"يورو", u"value": 0.23 }]

Months = [u"January", u"February", u"March", u"April", u"May", u"June", u"July", u"August", u"September", u"October", u"November", u"December"]
questions_list = []
answers_list = []
similarity_threshold = 0.6

@app.route("/")
@app.route("/home")
def home():
    with open("bag_of_intents.json", "r") as f:
        intents.bag_of_intents = json.load(f)

    #f = open("bag_of_intents.json", "r")
    #intents.bag_of_intents = json.load(f)
    #keys = f.read()
    #print(str(keys))
    #keys = keys.decode("utf-8")
    #intents.bag_of_intents = json.loads(keys)
    #f.close()

    #if os.path.isfile("bag_of_intents.json"):
    #    os.remove("bag_of_intents.json")

    #f = open("bag_of_intents.json","w")
    #json.dump(intents.bag_of_intents, f, ensure_ascii=False)
    #f.close()

    sample = [u"Hi", u"Hello", u"Hi, How are you", u"شلونك", u"شو أخبارك", u"عساكم بخير", u"حياكم الله", u"حياك الله", u"أهلا وسهلا", u"أهلا وسهلا يا حبيبي", 
              u"السلام عليكم", u"السلام عليكم عليكم ورحمة الله وبركاته", u"check how much money do i have Dirhams", u"show available money on my checking account", 
              u"show available money on my checking", u"how much money is available at my bank account", u"balance Dirhams", u"my balance", u"check my account Dirhams", 
              u"what's the balance in my checking account", u"what's the balance on my checking", u"show balance Dollar", u"check my checking account Euro", 
              u"check my checking", u"الرصيد في الحساب الجاري", u"المال في حسابي الجاري دولار", u"النقود في الحساب الجاري يورو", u"ممكن أشوف الرصيد حسابي الجاري درهم", 
              u"check how much money do i have in my savings account", u"check how much money do i have on my savings Euro", u"show available money in my savings account dollars", 
              u"show available money at my savings", u"how much money is available on my savings account", u"how much money is available on my savings", u"my savings account balance",
              u"savings balance dollars Dirhams", u"check my balance on savings account", u"check my balance on savings Euro", u"what's the balance in my savings account dollars", 
              u"what's the balance in my savings", u"show balance in savings", u"check my savings account", u"الرصيد في حساب المدخرات", u"الرصيد في حساب الادخاري دولار",
              u"النقود في حساب المدخر يورو", u"فرجني على رصيد حساب الادخار درهم", u"how much money i spent", u"how much money i spent bar", u"how much money i spent pie", 
              u"how much money i spent donut", u"show my expenses", u"show my expenses dollar bar", u"show my expenses pie", u"show my expenses donut", u"my expenses", 
              u"my expenses dollar bar", u"my expenses euro pie", u"my expenses dirham donut", u"my expenses dirhams bar", u"what's my expenses", u"what's my expenses bar", 
              u"what's my expenses dirham donut", u"what's my expenses bar euros", u"what's my expenses pie dollars", u"show expenses", u"show expenses pie dollar", 
              u"show expenses bar", u"show expenses dirham donut", u"check my expenses", u"check my expenses bar", u"check my expenses euro pie", u"check my expenses dirham donut", 
              u"إجمالي المصروفات", u"إجمالي المصروفات bar", u"إجمالي المصروفات pie دولار", u"مجموع مصروفات يورو donut", u"مجموع مصروفات bar", u"مجموع مصروفات درهم", 
              u"مجموع المصروف دولار", u"اجمالي مصروف pie", u"اجمالي مصروف يورو donut", u"مجموع نفقة", u"مجموع نفقة bar", u"اجمالي نفقات", u"اجمالي نفقات pie", 
              u"مجموع نفقاتي donut", u"مجموع نفقاتي", u"مجموع نفقاتي bar", u"how much loans", u"how much loans bar", u"how much loans dollar pie", u"how much loans bar dirham", 
              u"show my loans donut", u"show my loans bar", u"show my loans euro", u"my loans bar", u"my loans donut dollars", u"what's my loans pie", u"what's my loans", 
              u"show loans bar", u"show loans", u"check my loans donut", u"check my loans", u"إجمالى قسط", u"إجمالى قسط bar درهم", u"أقساط اجمالي pie", u"مجموع أقساطي يورو", 
              u"أقساط اجمالي donut", u"مجموع أقساطي", u"مجموع اقساطي bar", u"إجمالى الأقساط دولار", u"الأقساط اجمالي donut", u"مجموع الأقساط", u"مجموع الأقساط bar", u"إجمالى القسط دولار", 
              u"how much car expenditure", u"how much car expenditure bar dirham", u"how much car expenditure donut", u"show my car dollar pie", u"show my car", u"my car spend bar", 
              u"what's my car expenditure", u"show car bar pie", u"show car", u"my car spend donut", u"what's my car expenditure euro", u"check my car expenditure", 
              u"check my car expenditure dirhams donut", u"مجموع سيارتي درهم", u"سيارتى إجمالى bar", u"عربة مجموع يورو donut", u"العربة إجمالى يورو", u"سيارة درهم pie", 
              u"السيارة مجموع", u"إجمالي مجموع bar", u"اجمالي السيارة  درهم pie", u"إجمالى السيارة  يورو", u"how much food expenditure", u"how much food expenditure bar", 
              u"how much food expenditure pie", u"show my food dollars", u"show my food euro donut", u"show my food", u"my food spend bar", u"my food spend dirhams", 
              u"what's my food expenditure pie", u"what's my food expenditure donut", u"what's my food expenditure", u"show food bar", u"show food", u"check my food expenditure euro", 
              u"check my food expenditure", u"مجموع الأكل درهم", u"الطعام إجمالى bar", u"الطعام مجموع يورو donut", u"الطعام إجمالى يورو", u"الأكل درهم pie", u"الشراب مجموع", 
              u"إجمالي مجموع bar", u"اجمالي الشراب درهم pie", u"إجمالى الأكل يورو"]

    return render_template("index.html",
        title="Home Page",
        sample=sample,
        year=datetime.now().year)

@app.route("/statement")
def statement():
    return render_template("statement.html",
        title="Account Statement",
        CheckingAccount=CheckingAccount,
        SavingsAccount=SavingsAccount,
        year=datetime.now().year)

@app.route("/process_question", methods=["POST"])
def process_question():
    question = request.args.get("question")
    question.encode("utf-8")

    answer = ""
    chart_type = ""
    expected_questions = ""
    data = []
    chart_title = ""
    tooltip = ""

    bad_question = [u"I didn't get that. Can you say it again?", u"Sorry, can you tell me again?", u"Sorry, can you say that again?", 
                    u"I'm afraid I don't understand."]
    bad_question_ar = [u"عفواً, لم أفهم سيادتكم", u"آسف هل يمكنك السؤال مرة أخرى", u"لم أفهم السؤال سيدي", u"أخشى أني لم أفهم حضرتكم"]

    # Very long question or not English one => bad question
    if len(question) > 70:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer, similarity="")

    # print dynamic answer
    similarity = intents.get_all_similarity(question)
    if similarity[0]["value"] < similarity_threshold:
        answer = bad_question[random.randint(0, len(bad_question) - 1)] if not intents.is_arabic(question) else bad_question_ar[random.randint(0, len(bad_question_ar) - 1)]
        return jsonify(question=question, answer=answer, similarity=similarity)

    for intt in intents.bag_of_intents:
        if intt["intent"] == similarity[0]["intent"]:
            if not intents.is_arabic(question):
                answer = intt["answers"][random.randint(0, len(intt["answers"]) - 1)]
            else:
                answer = intt["answers_ar"][random.randint(0, len(intt["answers_ar"]) - 1)]
            break
    
    global DefaultCurrency
    global DefaultRate

    # Change Default Currency
    if question.lower().find(u"dollar") >= 0 or question.find(u"دولار") >= 0:
        DefaultCurrency = u"Dollars" if not intents.is_arabic(question) else u"دولار"
    elif question.lower().find(u"euro") >= 0 or question.find(u"يورو") >= 0:
        DefaultCurrency = u"Euro" if not intents.is_arabic(question) else u"يورو"
    elif question.lower().find(u"dirham") >= 0 or question.find(u"درهم") >= 0:
        DefaultCurrency = u"Dirhams" if not intents.is_arabic(question) else u"درهم"

    for cur in CurrencyRates:
        if DefaultCurrency == cur["name"] or DefaultCurrency == cur["name_ar"]:
            DefaultRate = cur["value"]

    if intents.is_arabic(question) and DefaultCurrency == u"Dirhams":
        DefaultCurrency = u"درهم"
    elif not intents.is_arabic(question) and DefaultCurrency == u"درهم":
        DefaultCurrency = u"Dirhams"

    if intents.is_arabic(question) and DefaultCurrency == u"Dollars":
        DefaultCurrency = u"دولار"
    elif not intents.is_arabic(question) and DefaultCurrency == u"دولار":
        DefaultCurrency = u"Dollars"

    if intents.is_arabic(question) and DefaultCurrency == u"Euro":
        DefaultCurrency = u"يورو"
    elif not intents.is_arabic(question) and DefaultCurrency == u"يورو":
        DefaultCurrency = u"Euro"

    # print Checking Account
    if similarity[0]["intent"] == u"balance_checking_account":
        answer += str(round(CheckingAccount[len(CheckingAccount) - 1]["Balance"] * DefaultRate, 2)) + " " + DefaultCurrency
    
    # print Savings Account
    if similarity[0]["intent"] == u"balance_savings_account":
        answer += str(round(SavingsAccount[len(SavingsAccount) - 1]["Balance"] * DefaultRate, 2)) + " " + DefaultCurrency

    # print expenses
    if similarity[0]["intent"] == u"expenses":
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat["Date"], dayfirst=True).month != startmonth:
                data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat["Date"], dayfirst=True).month
                monthly = 0.0

            if stat["Description"].find(u"expense") >= 0:
                total += stat["Debit"]
                monthly += stat["Debit"]

        data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + " " + DefaultCurrency

        chart_title = u"Total Expenses"
        tooltip = DefaultCurrency
        if question.find(u"bar") >= 0:
            chart_type = u"bar"
        elif question.find(u"pie") >= 0:
            chart_type = u"pie"
        elif question.find(u"donut") >= 0:
            chart_type = u"donut"

    # print loans
    if similarity[0]["intent"] == u"loans":
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat["Date"], dayfirst=True).month != startmonth:
                data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat["Date"], dayfirst=True).month
                monthly = 0.0

            if stat["Description"].find(u"loans") >= 0:
                total += stat["Debit"]
                monthly += stat["Debit"]

        data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + " " + DefaultCurrency

        chart_title = u"Total Loans"
        tooltip = DefaultCurrency
        if question.find(u"bar") >= 0:
            chart_type = u"bar"
        elif question.find(u"pie") >= 0:
            chart_type = u"pie"
        elif question.find(u"donut") >= 0:
            chart_type = u"donut"

    # print car
    if similarity[0]["intent"] == u"car":
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat["Date"], dayfirst=True).month != startmonth:
                data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat["Date"], dayfirst=True).month
                monthly = 0.0

            if stat["Description"].lower().find(u"car") >= 0:
                total += stat["Debit"]
                monthly += stat["Debit"]

        data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + " " + DefaultCurrency

        chart_title = u"Car Expenditure"
        tooltip = DefaultCurrency
        if question.find(u"bar") >= 0:
            chart_type = u"bar"
        elif question.find(u"pie") >= 0:
            chart_type = u"pie"
        elif question.find(u"donut") >= 0:
            chart_type = u"donut"

    # print food
    if similarity[0]["intent"] == u"food":
        monthly = 0.0
        total = 0.0
        startmonth = 1
        for stat in CheckingAccount:
            if parser.parse(stat["Date"], dayfirst=True).month != startmonth:
                data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
                startmonth = parser.parse(stat["Date"], dayfirst=True).month
                monthly = 0.0

            if stat["Description"].lower().find(u"food") >= 0:
                total += stat["Debit"]
                monthly += stat["Debit"]

        data.append({"name": Months[startmonth - 1], "count": round(monthly * DefaultRate, 2)})
        answer += str(round(total * DefaultRate, 2)) + " " + DefaultCurrency

        chart_title = u"Food Expenditure"
        tooltip = DefaultCurrency
        if question.find(u"bar") >= 0:
            chart_type = u"bar"
        elif question.find(u"pie") >= 0:
            chart_type = u"pie"
        elif question.find(u"donut") >= 0:
            chart_type = u"donut"
            
    questions_list.append(question)
    answers_list.append(answer)

    return jsonify(question=question,
                   unique_id=str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_" + str(datetime.now().hour) + "_" + str(datetime.now().minute) + "_" + str(datetime.now().second),
                   data=data,
                   chart_title=chart_title,
                   tooltip=tooltip,
                   chart_type=chart_type,
                   answer=answer,
                   similarity=similarity)
    
