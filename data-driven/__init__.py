from datetime import datetime
import logging
from modules.webhandler import WebhookHandler, InvalidSignatureError
from modules.openai import GptMessage,GPTddic
from modules.line import TextSendMessage
from modules import *
import azure.functions as func
from .api import *
import traceback
import json
from threading import Thread

cert = Certification('api_key.json')

handler = WebhookHandler(cert)
linebot = LineBotApi(cert)
google_search = GoogleSearch(cert)
chat_gpt = GPTddic(prompt='./prompt.json')


    
def create_gpt_messages(search,query):
    prompt:dict[str:str]=json.load(open('./prompt.json'))
    if not isinstance(search,list):
        search=[search]
    
    rlt=''
    for i in range(len(search)):
        rlt+=f'[{i+1}] {search[i]}\n'    
        
    context=prompt.get('user','')\
                    .replace('_query',query)\
                    .replace('_date',datetime.now().strftime('%Y-%m-%d'))\
                    .replace('_search',rlt)
    return [
        GptMessage('user',context)
    ]
    

@handler.intent('Inquire About Fraudulent TEL')
def search_tel(event, intent):
    result=[]
    tel=''
    for ele in intent.entities:
        if ele['category']=='TEL': 
            tel=ele['text']
            result=FraudulentTEL().get(tel).data
            break
    
    # chat_gpt.callback = lambda x: x['choices'][0]['message']['content']
    if len(result) != 0:
        res=TextSendMessage(text=f'根據查詢結果，{tel} 被回報是一個詐騙電話號碼。\n\r'+
                                '如果您收到了此電話，請勿透露個人信息並以任何方式回應，這可能會導致您被騙取金錢或其他財物。\n\r'+
                                '如果您已經受到損失，應立即向當地警方報告，提供所有相關證據。\n\r'+
                                '如果您需要進一步的幫助，可以更詳細說明您的狀況。\n\r'+ 
                                '另外提醒大家，請務必保持警覺，不要輕信來自陌生人的信息和電話，需要採取一些防範措施來避免被詐騙。\n\r'+
                                '(來源: https://https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢{tel}並不存在於資料庫中，但仍有可能需要注意此號碼。')
        
    linebot.reply_message(event['replyToken'], res)

@handler.intent('Inquire About Fraudulent ID')
def search_id(event, intent):
    result=[]
    id=''
    print(intent.entities)
    for lineId in intent.entities:
        if lineId['category']=='lineId': 
            id=lineId['text']
            result=FraudulentID().get(id).data
            break
    if len(result)!=0:
        res=TextSendMessage(text=f'根據查詢結果，{id} 被回報是一個詐騙帳號。\n\r'+
                                '如果您收到了此帳號的訊息，請勿透露個人信息並以任何方式回應，這可能會導致您被騙取金錢或其他財物。\n\r'+
                                '如果您已經受到損失，應立即向當地警方報告，提供所有相關證據。\n\r'+
                                '如果您需要進一步的幫助，可以更詳細說明您的狀況。\n\r'+
                                '另外提醒大家，請務必保持警覺，不要輕信來自陌生人的信息和電話，需要採取一些防範措施來避免被詐騙。\n\r'+
                                '(來源: https://https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢{id}並不存在於資料庫中，但仍有可能需要注意此帳號。')
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Inquire About Fraudulent URL')
def search_url(event, intent):
    result=[]
    url=''
    for url in intent.entities:
        if url['category']=='URL': 
            url=url['text']
            result=FraudulentURL().get(url).data
            break
    if len(result)!=0:
        res=TextSendMessage(text=f'根據查詢結果，{url} 被回報是一個詐騙網站。\n\r'+
                                '如果您收到了此網站的訊息，請勿透露個人信息並以任何方式回應，這可能會導致您被騙取金錢或其他財物。\n\r'+
                                '如果您已經受到損失，應立即向當地警方報告，提供所有相關證據。\n\r'+
                                '如果您需要進一步的幫助，可以更詳細說明您的狀況。\n\r'+
                                '另外提醒大家，請務必保持警覺，不要輕信來自陌生人的信息和電話，需要採取一些防範措施來避免被詐騙。\n\r'+
                                '(來源: https://https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢{url}並不存在於資料庫中，但仍有可能需要注意此網站。')
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Other Inquiries')
def custom_search(event, intent):
    user_query = event['message']['text']
    
    

    # Google搜尋
    result=google_search.get(user_query).data
    print(result)
    
    chat_gpt.callback=lambda x:x['data']
    chat_gpt.send_messages(create_gpt_messages(result,user_query))
    reply=chat_gpt.get_reply()\
                    .replace('。','。\n\r')\
                    .replace('：','：\n\r')\
                    .replace(')[',')\n\r[')
                    
    linebot.reply_message(event['replyToken'], TextSendMessage(text=reply))


@handler.intent('None')
def none_intent(event, intent):
    linebot.reply_message(event['replyToken'], TextSendMessage(text='抱歉，我不太懂您的意思，請再說一次'))


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        if req.method != 'POST':
            return func.HttpResponse(f'Response from {__name__}', status_code=200)

        signature = req.headers['X-Line-Signature']
        req_body = req.get_body()

        logging.info(
            f'Request headers:{dict(req.headers)} \n Request body: {req.get_json()}')
    
        handler.handle(req_body, signature)
    except InvalidSignatureError as e:
        logging.info(e)
    except ValueError:
        logging.info(traceback.format_exc())
    except Exception:
        logging.info(traceback.format_exc())

    return 'ok'
