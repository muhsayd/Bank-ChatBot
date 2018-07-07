# -*- coding: utf-8 -*-

from langdetect import detect
import spacy
import operator
import json

nlp = spacy.load("en")

arabic_letters = [u"ا", u"أ", u"آ", u"إ", u"ء", u"ب", u"ت", u"ـ", u"ث", u"ج", u"ح", u"خ", u"د", u"ذ", u"ر", u"ز", u"س", u"ش", u"ص", 
                  u"ض", u"ط", u"ظ", u"ع", u"غ", u"ف", u"ق", u"ك", u"ل", u"م", u"ن", u"ه", u"و", u"ؤ", u"ة", u"ئ", u"ي", u"ي"]

#bag_of_intents = []
bag_of_intents = [{
                      u"intent": u"hi", 
                      u"values": [u"hi", u"hello", u"welcome", u"what's up"],
                      u"keywords": [u"hi", u"hello"],
                      u"keywords_ar": [u"هلا", u"أهلا", u"اهلا", u"وسهلا", u"حيا", u"حياكم", u"مرحبا", u"السلام", u"عليكم", u"ورحمه", u"رحمه", u"ورحمة", u"رحمة", u"الله", 
                                       u"وبركاته", u"بركاته", u"وبركاتة", u"بركاتة", u"يا"],
                      u"answers": [u"Hi, how can I help you ?", u"Hello, Welcome to BankBot by Stallion.ai.", u"How can I help you ?", 
                                   u"Welcome, Thanks for choosing BankBot by Stallion.ai."],
                      u"answers_ar": [u"هلا, كيف أستطيع خدمتك ؟", u"مرحبا بك في نظام ستاليون الخبير", u"أهلا وسهلا في نظام المحادثة الخبيرة", 
                                      u"شكراً لاستخدامكم نظام ستاليون الخبير"]
                  },
                  {
                      u"intent": u"how_are_you",
                      u"values": [u"how are you", u"how are you ?", u"hi, how are you ?", u"hello, how are you ?"],
                      u"keywords_ar": [u"كيف", u"حالك", u"شلونك", u"شو", u"اخبارك", u"أخبارك", u"عساكم", u"بخير", u"أنت", u"انت", u"أزيك", u"ازيك", u"إزيك", u"عامل", u"ايه", u"إيه", u"أيه", u"كويس"],
                      u"answers": [u"Doing great, thanks.", u"I am fine thank you", u"How can I help you ?", u"Feeling wonderful!"],
                      u"answers_ar": [u"أنا بخير, شكراً لك", u"الحمد لله أنا بخير", u"شكراً, كيف أستطيع مساعدتك", u"شكراً, كيف أستطيع خدمتك"]
                  },
                  {
                      u"intent": u"thanks",
                      u"values": [u"thank", u"thanks", u"thank you", u"many thanks", u"Thank you so much", u"thankful", u"grateful", u"glade to see you"],
                      u"keywords_ar": [u"شكرا", u"شكر", u"تحية", u"تحياتي", u"شاكر", u"مشكور", u"سررت", u"بك", u"سعدت", u"جدا", u"اشكرك", u"أشكرك", u"جزيلا"],
                      u"answers": [u"You are Welcome!", u"Thanks.", u"Anytime. That's what I'm here for.", u"It's my pleasure to help.", u"My pleasure."],
                      u"answers_ar": [u"شكراً لك", u"شكراً على لطفك", u"لا شكر على واجب", u"على الرحب والسعة سيدي", u"العفو يا سيدي", 
                                      u"سعدت بصحبتك", u"شكراً جزيلا", u"وأنا أيضا سررت بخدمتك", u"مرحبا بك في أي وقت سيدي"]
                  },
                  {
                      u"intent": u"balance_checking_account",
                      u"values": [u"check how much money do i have", u"show available money on my checking account",
                                  u"show available money on my checking", u"how much money is available at my bank account", u"balance", u"my balance", u"check my account", 
                                  u"what's the balance in my checking account", u"what's the balance on my checking", u"show balance", u"check my checking account", u"check my checking"],
                      u"keywords": [u"checking", u"checking account"],
                      u"keywords_ar": [u"الحساب", u"الجاري", u"جاري", u"حساب", u"الرصيد", u"رصيدي", u"رصيد", u"المال", u"النقود", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your balance in Checking Account is: "],
                      u"answers_ar": [u"رصيدك في الحساب الجاري هو: "]
                  },
                  {
                      u"intent": u"balance_savings_account",
                      u"values": [u"check how much money do i have in my savings account", u"check how much money do i have on my savings", 
                                  u"show available money in my savings account", u"show available money at my savings", 
                                  u"how much money is available on my savings account", u"how much money is available on my savings", u"my savings account balance",
                                  u"savings balance", u"check my balance on savings account", u"check my balance on savings", 
                                  u"what's the balance in my savings account", u"what's the balance in my savings", u"show balance in savings", 
                                  u"check my savings account"],
                      u"keywords": [u"savings", u"savings account"],
                      u"keywords_ar": [u"الحساب", u"حساب", u"المدخرات", u"مدخرات", u"ادخار", u"الادخار", u"الادخاري", u"الادخارى", u"المدخر", u"مدخر", u"الرصيد", u"رصيدي", u"رصيد", u"المال", u"النقود", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your balance in Savings Account is: "],
                      u"answers_ar": [u"رصيدك في المدخرات هو: "]
                   },
                   {
                      u"intent": u"expenses",
                      u"values": [u"how much money i spent", u"show my expenses", u"my expenses", u"what's my expenses", u"show expenses", u"check my expenses"],
                      u"keywords": [u"expense", u"expenses"],
                      u"keywords_ar": [u"المصروفات", u"مصروفات", u"المصروف", u"مصروف", u"نفقة", u"نفقات", u"نفقاتي", u"إجمالي", u"اجمالي", u"إجمالى", u"اجمالى", u"مجموع", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your total expenses is: "],
                      u"answers_ar": [u"إجمالي مصروفاتك هو: "]
                   },
                   {
                      u"intent": u"loans",
                      u"values": [u"how much loans", u"show my loans", u"my loans", u"what's my loans", u"show loans", u"check my loans"],
                      u"keywords": [u"loan", u"loans"],
                      u"keywords_ar": [u"قسط", u"أقساط", u"أقساطي", u"اقساطي", u"اقساطي", u"إجمالي", u"اجمالي", u"إجمالى", u"اجمالى", u"مجموع", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your total loans is: "],
                      u"answers_ar": [u"إجمالي أقساطك هي: "]
                   },
                   {
                      u"intent": u"car",
                      u"values": [u"how much car expenditure", u"show my car", u"my car spend", u"what's my car expenditure", u"show car", u"check my car expenditure"],
                      u"keywords": [u"car", u"cars"],
                      u"keywords_ar": [u"سيارتي", u"سيارتى", u"عربة", u"العربة", u"سيارة", u"السيارة", u"إجمالي", u"اجمالي", u"إجمالى", u"اجمالى", u"مجموع", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your car expenditure is: "],
                      u"answers_ar": [u"إجمالي نفقات السيارة هي: "]
                   },
                   {
                      u"intent": u"food",
                      u"values": [u"how much food expenditure", u"show my food", u"my food spend", u"what's my food expenditure", u"show food", u"check my food expenditure"],
                      u"keywords": [u"food", u"foods"],
                      u"keywords_ar": [u"الشرب", u"الشراب", u"الأكل", u"أكل", u"طعام", u"الطعام", u"إجمالي", u"اجمالي", u"إجمالى", u"اجمالى", u"مجموع", u"دولار", u"يورو", u"درهم"],
                      u"answers": [u"your food expenditure is: "],
                      u"answers_ar": [u"إجمالي نفقات الطعام والشراب هو: "]
                   }]

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

    qust = nlp(question.lower())
    
    for intent in bag_of_intents:
        similarity = []

        print("is arabic: " + str(is_arabic(question)))

        if not is_arabic(question):
            for i in intent[u"values"]:
                doc = nlp(i)
                similarity.append(qust.similarity(doc))
        else:
            matched = 0
            for i in intent[u"keywords_ar"]:
                for j in question.split():
                    if j == i:
                        matched += 1

            if matched >= 0:
                print("Equation Before : " + str(float(matched)/float(len(question.split()))))
                similarity.append(float(matched)/float(len(question.split())))
                similarity.append(float(matched)/float(len(question.split())))
                print("Equation After : " + str(similarity))
            else:
                similarity.append(0.0)
                similarity.append(0.0)

            
        # explicit keyword mention means more weight to the intent
        if u"keywords" in intent:
            for i in intent[u"keywords"]:
                if question.lower().find(i) >= 0:
                    similarity = [s * 1.3 for s in similarity]
                    print("keywords: " + str(similarity))
                    break

        # if question is not english decrease weights of similarity
        if detect(question) != u"en" and not is_arabic(question):
            similarity = [s * 0.7 for s in similarity]
            print("detect(question): " + str(similarity))

        if is_arabic(question):
            similarity = [s * 1.2 for s in similarity]
            print("is_arabic(question): " + str(similarity))

        similarity = sorted(similarity, reverse=True)
        print("sorted: " + str(similarity))
        results.append({ u"intent": intent[u"intent"], u"value": (similarity[0] + similarity[1]) / 2.0 })

    results = sorted(results, key=operator.itemgetter(u"value"), reverse=True)
    return results

def is_arabic(phrase):
    for i in arabic_letters:
        if phrase.find(i) > 0:
            return True
    return False