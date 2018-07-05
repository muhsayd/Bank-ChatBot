
from langdetect import detect
import spacy
import operator

nlp = spacy.load('en')

arabic_letters = ['ا', 'أ', 'آ', 'إ', 'ء', 'ب', 'ت', 'ـ', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 
                  'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ؤ', 'ة', 'ئ', 'ي', 'ي']

bag_of_intents = [{
                      'intent': 'hi', 
                      'values': ['hi', 'hello'],
                      'keywords': ['hi', 'hello'],
                      'keywords_ar': ['هلا', 'أهلا', 'اهلا', 'حيا', 'حياكم', 'مرحبا', 'السلام', 'عليكم', 'ورحمه', 'رحمه', 'ورحمة', 'رحمة', 'الله', 
                                      'وبركاته', 'بركاته', 'وبركاتة', 'بركاتة', 'يا'],
                      'answers': ['Hi, how can I help you ?', 'Hello, Welcome to BankBot by Stallion.ai.', 'How can I help you ?', 
                                  'Hello, and thanks for choosing BankBot by Stallion.ai.'],
                      'answers_ar': ['هلا, كيف أستطيع خدمتك ؟', 'مرحبا بك في نظام ستاليون الخبير', 'أهلا وسهلا في نظام المحادثة الخبيرة', 
                                  'شكراً لاستخدامكم نظام ستاليون الخبير']
                  },
                  {
                      'intent': 'how_are_you',
                      'values': ['how are you','how are you ?', 'hi, how are you ?', 'hello, how are you ?'],
                      'keywords_ar': ['كيف', 'حالك', 'شلونك', 'شو', 'اخبارك', 'أخبارك', 'عساكم', 'بخير', 'أنت', 'انت'],
                      'answers': ['Doing great, thanks.', 'I am fine thank you', 'How can I help you ?', 'Feeling wonderful!'],
                      'answers_ar': ['أنا بخير, شكراً لك', 'الحمد لله أنا بخير', 'شكراً, كيف أستطيع مساعدتك', 'شكراً, كيف أستطيع خدمتك']
                  },
                  {
                      'intent': 'thanks',
                      'values': ['thank', 'thanks', 'thank you', 'many thanks', 'Thank you so much', 'thankful', 'grateful'],
                      'keywords_ar': ['شكرا', 'شكر', 'تحية', 'تحياتي', 'شاكر', 'مشكور'],
                      'answers': ['You are Welcome!', 'Thanks.', "Anytime. That's what I'm here for.", "It's my pleasure to help.", "My pleasure."],
                      'answers_ar': ['شكراً لك', 'شكراً على لطفك', 'لا شكر على واجب', 'على الرحب والسعة سيدي', 'العفو يا سيدي']
                  },
                  {
                      'intent': 'welcome',
                      'values': ['welcome', 'glade to see you', "what's up"],
                      'keywords': ['welcome'],
                      'keywords_ar': ['مرحبا', 'سررت', 'بك', 'الجديد', 'ما', 'سعدت'],
                      'answers': ['Welcome to BankBot by Stallion.ai.', 'Welcome and thanks for choosing BankBot by Stallion.ai.', 'How can I help you ?'],
                      'answers_ar': ['سعدت بصحبتك', 'شكراً جزيلا', 'وأنا أيضا سررت بخدمتك', 'مرحبا بك في أي وقت سيدي']
                  },
                  {
                      'intent': 'balance_checking_account',
                      'values': ['check how much money do i have', 'show available money on my checking account',
                                 'show available money on my checking', 'how much money is available at my bank account', 'balance', 'my balance', 'check my account', 
                                 "what's the balance in my checking account", "what's the balance on my checking", 'show balance', 'check my checking account', 'check my checking'],
                      'keywords': ['checking', 'checking account'],
                      'keywords_ar': ['الحساب', 'الجاري', 'جاري', 'حساب', 'الرصيد', 'رصيدي', 'رصيد', 'المال', 'النقود', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your balance in Checking Account is: '],
                      'answers_ar': ['رصيدك في الحساب الجاري هو: ']
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
                      'keywords_ar': ['الحساب', 'حساب', 'المدخرات', 'مدخرات', 'ادخار', 'المدخر', 'مدخر', 'الرصيد', 'رصيدي', 'رصيد', 'المال', 'النقود', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your balance in Savings Account is: '],
                      'answers_ar': ['رصيدك في المدخرات هو: ']
                   },
                   {
                      'intent': 'expenses',
                      'values': ['how much money i spent', 'show my expenses', 'my expenses', "what's my expenses", 'show expenses', 'check my expenses'],
                      'keywords': ['expense', 'expenses'],
                      'keywords_ar': ['المصروفات', 'مصروفات', 'المصروف', 'مصروف', 'نفقة', 'نفقات', 'نفقاتي', 'إجمالي', 'اجمالي', 'إجمالى', 'اجمالى', 'مجموع', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your total expenses is: '],
                      'answers_ar': ['إجمالي مصروفاتك هو: ']
                   },
                   {
                      'intent': 'loans',
                      'values': ['how much loans', 'show my loans', 'my loans', "what's my loans", 'show loans', 'check my loans'],
                      'keywords': ['loan', 'loans'],
                      'keywords_ar': ['قسط', 'أقساط', 'أقساطي', 'اقساطي', 'اقساطي', 'إجمالي', 'اجمالي', 'إجمالى', 'اجمالى', 'مجموع', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your total loans is: '],
                      'answers_ar': ['إجمالي أقساطك هي: ']
                   },
                   {
                      'intent': 'car',
                      'values': ['how much car expenditure', 'show my car', 'my car spend', "what's my car expenditure", 'show car', 'check my car expenditure'],
                      'keywords': ['car', 'cars'],
                      'keywords_ar': ['سيارتي', 'سيارتى', 'عربة', 'العربة', 'سيارة', 'السيارة', 'إجمالي', 'اجمالي', 'إجمالى', 'اجمالى', 'مجموع', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your car expenditure is: '],
                      'answers_ar': ['إجمالي نفقات السيارة هي: ']
                   },
                   {
                      'intent': 'food',
                      'values': ['how much food expenditure', 'show my food', 'my food spend', "what's my food expenditure", 'show food', 'check my food expenditure'],
                      'keywords': ['food', 'foods'],
                      'keywords_ar': ['الشرب', 'الشراب', 'الأكل', 'أكل', 'طعام', 'الطعام', 'إجمالي', 'اجمالي', 'إجمالى', 'اجمالى', 'مجموع', 'دولار', 'يورو', 'درهم'],
                      'answers': ['your food expenditure is: '],
                      'answers_ar': ['إجمالي نفقات الطعام والشراب هو: ']
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

    qust = nlp(question)
    
    for intent in bag_of_intents:
        similarity = []

        if not is_arabic(question):
            for i in intent['values']:
                doc = nlp(i)
                similarity.append(qust.similarity(doc))
        else:
            matched = 0
            for i in intent['keywords_ar']:
                for j in question.split():
                    if j == i:
                        matched += 1

            if matched >= 0:
                similarity.append(matched/len(question.split()))
                similarity.append(matched/len(question.split()))
            else:
                similarity.append(0)
                similarity.append(0)

            
        # explicit keyword mention means more weight to the intent
        if 'keywords' in intent:
            for i in intent['keywords']:
                if question.find(i) >= 0:
                    similarity = [s * 1.3 for s in similarity]
                    break

        # if question is not english decrease weights of similarity
        if detect(question) != 'en' and not is_arabic(question):
            similarity = [s * 0.7 for s in similarity]

        similarity = sorted(similarity, reverse=True)
        results.append({ 'intent': intent['intent'], 'value': (similarity[0] + similarity[1]) / 2 })

    results = sorted(results, key=operator.itemgetter('value'), reverse=True)
    return results

def is_arabic(phrase):
    for i in arabic_letters:
        if phrase.find(i) > 0:
            return True
    return False