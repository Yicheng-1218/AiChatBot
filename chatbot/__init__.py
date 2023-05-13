import azure.functions as func
import logging
from modules.webhandler import WebhookHandler, InvalidSignatureError
from modules.line import TextSendMessage
from modules.chat_gpt import GptMessage
from modules import *
from .api_resource import *


cert=Certification('api_key.json')

handler = WebhookHandler(cert)
linebot=LineBotApi(cert)
gpt=ChatGPT(cert)
google_search=GoogleSearch(cert)

    
@handler.intent('Inquire About Fraudulent TEL')
def search_tel(event, intent):
    result=[]
    tel=''
    for ele in intent.entities:
        if ele['type']=='TEL': 
            tel:str=ele['value']
            if tel.startswith('0'):
                tel=tel.replace('0','+886',1)
            result=FraudulentTEL.get(tel)
            break
        
    if tel=='':
        res=TextSendMessage(text=f'請問您是想詢問詐騙電話嗎? 請提供電話號碼哦。')
        return linebot.reply_message(event['replyToken'], res)
    
    if len(result)>0:
        res=TextSendMessage(text=f'{tel} 被回報是一個詐騙電話號碼。\
            \r\n切記請勿隨意向他人提供相關個人資訊，包括但不限於身分證字號、銀行帳號、信用卡卡號、網路帳號、密碼、生日、住址、電話號碼、電子郵件地址等。\
            \r\n(來源: https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢{tel}並不存在於資料庫中，但仍有可能需要注意此號碼。')
        
    linebot.reply_message(event['replyToken'], res)



        
@handler.intent('Inquire About Fraudulent ID')
def search_id(event, intent):
    result=[]
    id=''
    for id in intent.entities:
        if id['type']=='LineID': 
            id=id['value']
            result=FraudulentID.get(id)
            break
    
    if id=='':
        res=TextSendMessage(text=f'請問您是想詢問詐騙LineID嗎? 請提供LineID哦。')
        return linebot.reply_message(event['replyToken'], res)    
    
    if len(result)>0:
        res=TextSendMessage(text=f'{id}\n被回報是一個詐騙LineID。\n\r(來源: https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢({id})並不存在於資料庫中，但仍有可能需要注意此LineID。\
           \r\n請勿隨意向他人提供相關個人資訊，包括但不限於身分證字號、銀行帳號、信用卡卡號、網路帳號、密碼、生日、住址、電話號碼、電子郵件地址等。')
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Inquire About Fraudulent URL')
def search_url(event, intent):
    result=[]
    url=''
    for url in intent.entities:
        if url['type']=='URL': 
            url=url['value']
            result=FraudulentURL.get(url)
            break
        
    if url=='':
        res=TextSendMessage(text=f'請問您是想詢問詐騙網站嗎? 請提供網址哦。')
        return linebot.reply_message(event['replyToken'], res)    

        
    if len(result)>0:
        res=TextSendMessage(text=f'({url})\n被回報是一個詐騙網站。\n\r(來源: https://165.npa.gov.tw/)')
    else:
        trust_score=Urlvoid.get(url)
        if trust_score!=Urlvoid.DOMAIN_NOT_FOUND:
            res=TextSendMessage(text=f'經系統查詢\n({url})\n並不存在於警政資料庫中，但經過網站信任度分析，此網站信任度為{trust_score}。\n(來源: {Urlvoid.url})')
        else:
            res=TextSendMessage(text=f'經系統查詢({url})並不存在於資料庫中，但仍有可能需要注意此網站。')
            
    
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Other Inquiries')
def custom_search(event, _):
    user_query = event['message']['text']
    
    # Google搜尋
    resp_normal=google_search.normal_search(user_query,advanced=True,num_results=3)
    resp_custom=google_search.custom_search(user_query,advanced=True,num_results=3)
    
    resp_normal=resp_normal if resp_normal is not None else []
    resp_custom=resp_custom if resp_custom is not None else []
    data=set(list(resp_normal)+list(resp_custom))
    if len(data)!=0:
        result = ''.join([f'[{i+1}]{k.title}\n{k.description}\nURL:{k.url}\n\n' for i,k in enumerate(data)])
    else:
        result='查無相關資訊'
    logging.info(result)
    
    
    # GPT訊息生成
    prompt=f"""
    You will act like a legal advisor in a law firm.
    Your task is to provide assistance to users based on the search results between the three backticks.

    Your answer should include the following:
    - List solutions steps by steps to solve the problem. <if applicable>
    - Other relevant suggestions.
    - Provide reference results at the end of the response, only use the search results between the three backticks and
      listing a maximum of three references if there are more than three.
    - Format the reference links in the following format: [1](url) ...
    - Response in Traditional Chinese.

    search results: ```{result}```

    user: {user_query}

    """
    reply=gpt.create_completion(GptMessage('user',prompt),temperature=0.2)
    linebot.reply_message(event['replyToken'], TextSendMessage(text=reply))


@handler.intent('None')
def none_intent(event, intent):
    user_query:str = event['message']['text']
    if max([i in user_query.lower() for i in ['你好','hi','嗨','哈囉','hello','哈摟','hey','嘿']]):
        return linebot.reply_message(event['replyToken'],TextSendMessage(text='你好，請問有什麼可以幫助您的?'))
    linebot.reply_message(event['replyToken'],
        TextSendMessage(text='抱歉，我不太懂您的意思，請再說一次'))
    
        
@handler.default()
def default(event):
    linebot.reply_message(event['replyToken'],
        TextSendMessage(text='出了一點小錯，你剛剛說甚麼?'))    



def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if req.method != 'POST':
            return func.HttpResponse(f'Response from {__name__}', status_code=200)

        signature = req.headers['X-Line-Signature']
        req_body = req.get_body()

        logging.info(
            f'Request headers:{dict(req.headers)} \n Request body: {req.get_json()}')
    
        handler.handle(req_body, signature)
    except InvalidSignatureError as e:
        logging.error(e)

    return 'ok'
