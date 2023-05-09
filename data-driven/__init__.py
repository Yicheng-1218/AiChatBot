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
from concurrent.futures import ProcessPoolExecutor

cert = Certification('api_key.json')

handler = WebhookHandler(cert)
linebot = LineBotApi(cert)
google_search = GoogleSearch(cert)
chat_gpt = GPTddic(prompt='./prompt.json',callback=lambda x:x['data'])


    
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
    user_query = event['message']['text']
    result=[]
    tel=''
    for ele in intent.entities:
        if ele['category']=='TEL': 
            tel=ele['text']
            result=FraudulentTEL().get(tel).data
            break
    
    # chat_gpt.callback = lambda x: x['choices'][0]['message']['content']
    if len(result) != 0:
        # result=f'{tel} 被回報是一個詐騙電話號碼。\n\r(來源: https://165.npa.gov.tw/)'
        # chat_gpt.send_messages(create_gpt_messages(result,user_query))
        res=TextSendMessage(text=f'{tel} 被回報是一個詐騙電話號碼。\n\r(來源: https://165.npa.gov.tw/)')
    else:
        res=TextSendMessage(text=f'經系統查詢{tel}並不存在於資料庫中，但仍有可能需要注意此號碼。')
        
    linebot.reply_message(event['replyToken'], res)



        
@handler.intent('Inquire About Fraudulent ID')
def search_id(event, intent):
    user_query = event['message']['text']
    # result=[]
    # id=''
    # relist=re.findall(r'@?[a-zA-z0-9(.-_)]{4,}', user_query)
    
    # TODO: 這裡要改成多執行緒
    # def search_id(id):
    #     url='https://165.npa.gov.tw/api/queryLineId/'
    #     try:
    #         return requests.get(url+id).json()
    #     except:
    #         return []    
    # with ProcessPoolExecutor() as executor:
    #     for i in executor.map(search_id,relist):
    #         result.append(i)
    
    
    # if max([len(e) for e in result]) > 0:
    #     for i in result:
    #         try:
    #             id=i[0].get('lineId')
    #         except:
    #             pass
    #     result=f'{id} 被回報是一個詐騙帳號。\n\r(來源: https://165.npa.gov.tw/)'
    #     print(result)
    #     chat_gpt.send_messages(create_gpt_messages(result,user_query))
    #     res=TextSendMessage(text=chat_gpt.get_reply())
    # else:
    #     res=TextSendMessage(text=f'經系統查並不存在於資料庫中，但仍有可能需要注意此帳號。')
    res=TextSendMessage(text=f'此功能維修中')
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Inquire About Fraudulent URL')
def search_url(event, intent):
    user_query = event['message']['text']
    result=[]
    url='url'
    for url in intent.entities:
        if url['category']=='URL': 
            url=url['text']
            result=FraudulentURL().get(url).data
            break
        
        
    if len(result)!=0:
        # result=f'({url})\n被回報是一個詐騙網站。\n\r(來源: https://165.npa.gov.tw/)'
        # chat_gpt.send_messages(create_gpt_messages(result,user_query))
        
        res=TextSendMessage(text=f'({url})\n被回報是一個詐騙網站。\n\r(來源: https://165.npa.gov.tw/)')
    else:
        urlvoid=Urlvoid()
        trust_score=urlvoid.get(url)
        if trust_score!=urlvoid.DOMAIN_NOT_FOUND:
            res=TextSendMessage(text=f'經系統查詢\n({url})\n並不存在於警政資料庫中，但經過網站信任度分析，此網站信任度為{trust_score}。\n(來源: {urlvoid.url})')
        else:
            res=TextSendMessage(text=f'經系統查詢({url})並不存在於資料庫中，但仍有可能需要注意此網站。')
            
    
    linebot.reply_message(event['replyToken'], res)


@handler.intent('Other Inquiries')
def custom_search(event, intent):
    user_query = event['message']['text']
    
    

    # Google搜尋
    result=google_search.get(user_query).data
    logging.info(result)
    
    chat_gpt.send_messages(create_gpt_messages(result,user_query))
    reply=chat_gpt.get_reply()\
                    .replace('。','。\n\r')\
                    .replace('：','：\n\r')\
                    .replace(')[',')\n\r[')
                    
    linebot.reply_message(event['replyToken'], TextSendMessage(text=reply))


@handler.intent('None')
def none_intent(event, intent):
    ref={
        'Inquire About Fraudulent TEL':'詢問詐騙電話',
        'Inquire About Fraudulent ID':'詢問詐騙帳號',
        'Inquire About Fraudulent URL':'詢問詐騙網站',
        'Other Inquiries':'詢問謠言或是詐騙訊息'
    }
    
    suffix=ref.get(intent.intents[0]['category']) if intent.intents[0]['confidenceScore']>0.8 else None
    
        
    if suffix is None:
        linebot.reply_message(event['replyToken'], TextSendMessage(text='抱歉，我不太懂您的意思，請再說一次'))
    linebot.reply_message(event['replyToken'], TextSendMessage(text=f'抱歉，我不太懂您的意思，您是想{suffix}嗎? 可以詳細再說明一次給我哦'))
    
        


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
