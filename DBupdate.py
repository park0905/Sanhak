import os
import json
import googleapiclient.discovery
from collections import defaultdict
import boto3
import keyboard
import sys
from datetime import datetime

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

global idle
global nametable
global percent
############ Youtube ##################### ###############
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "" # 개인 debeloper_key @@Youtube

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
############### ############### ############### ############### 


############   AWS  ##################### ############### 
translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl = True)
client = boto3.client('comprehend')



client_dynamo = boto3.client('dynamodb')

############### ############### ############### ############### 

cnt1=cnt2=cnt3=cnt4=cnt5=cnt6=cnt7=0
idle = 0
def videosRequest(categoryId, maxResults, la):
    if keyboard.is_pressed('q'):  # stop!!!!!!
        sys.exit()
    request = youtube.videos().list(
    part="snippet",
    chart="mostPopular",
    maxResults=maxResults,
    regionCode="KR",
    videoCategoryId=categoryId
    ).execute()
    results = request.get('items', [])
    labee = la
    for i in range(0, maxResults):
        title = results[i]['snippet']['title']
        videoid = results[i]['id']
        print(title + " : " + videoid)
        commentManage(i, videoid, title, labee)


def searchRequest(channelId, maxResults, order, query, la):
    if keyboard.is_pressed('q'):  # stop!!!!!!
        sys.exit()
    request = youtube.search().list(
    part="snippet",
    channelId=channelId,
    maxResults=maxResults,
    order=order,
    q=query,
    regionCode="KR"
    ).execute()
    results = request.get('items', [])
    labe = la
    for i in range(0, len(results)):
        if results[i]['id']['kind'] == 'youtube#video' :
            title = results[i]['snippet']['title']
            videoid = results[i]['id']['videoId']
            print(title + " : " + videoid)
            if labe == 3:
                global cnt3
                cnt3+=1
                client_dynamo.put_item(
                    TableName='ALLMOVIE',
                    Item = {
                        'id' : {
                            'S' : str(cnt3)
                            },
                        'Mixed' : {
                            'S' : '0'
                            },
                        'Negative' : {
                            'S' : '0'
                            },
                        'Neutral' : {
                            'S' : '0'
                            },
                        'Positive' : {
                            'S' : '0'
                            },
                        'Sentiment' : {
                            'S' : '0'
                            },
                        'Title' : {
                            'S' : title
                            },
                        'Vid' : {
                            'S' : videoid
                        }
                    }
                )
            else:
                commentManage(i, videoid, title, labe)
        elif results[i]['id']['kind'] == 'youtube#playlist':
            title = results[i]['snippet']['title']
            playlistid = results[i]['id']['playlistId']
            print(title + " : " + playlistid)
            commentManage(i, playlistid, title, labe)

def commentManage(index, vid, title, la):
    if keyboard.is_pressed('q'):  # stop!!!!!!
        sys.exit()
    global cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7
    global percent
    request = youtube.commentThreads().list(
        part="snippet",
        order="relevance",
        textFormat="plainText",
        videoId=vid,
        maxResults="10"
    )
    lll = la
    try:
        response = request.execute()
        responseStr = 'a'
        for aa in range(0, 10):
            response_review = response['items'][aa]['snippet']['topLevelComment']['snippet']['textDisplay']
            print(response_review)
            responseStr += response_review
            responseStr += '. '

        ###############  AWS Translate ###### ############### 
        result = translate.translate_text(Text=responseStr, SourceLanguageCode="ko", TargetLanguageCode="en")
        transText = result.get('TranslatedText')
        ############### ############### ###############



        ############### AWS Comprehend ############### ###############  
        resultSent = client.detect_sentiment(
            Text= transText,
            LanguageCode='en'
        )
        
        percent = resultSent['SentimentScore']
        totalSent = resultSent['Sentiment']
        ############### ###############   ############### ###############  


        print(percent) ## 감정 스코어
        print(totalSent) ## 현재 감정

        if lll == 1:
            nametable = 'PVIDEO'
            cnt1 += 1
            if cnt1 == 21:
                cnt1 = 1
            CNT = cnt1
        
        elif lll ==2:
            nametable = 'PMUSIC'
            print(nametable)
            cnt2 +=1
            if cnt2 == 21:
                cnt2 = 1
            CNT = cnt2
         
        elif lll ==3:
            nametable = 'ALLMOVIE'
            print(nametable)
            cnt3 +=1
            if cnt3 == 21:
                cnt3 = 1
            CNT = cnt3
            
        elif lll ==4:
            nametable = 'SVIDEO'
            print(nametable)
            cnt4 +=1
            if cnt4 == 21:
                cnt4 = 1
            CNT = cnt4
       
        elif lll ==5:
            nametable = 'SMUSIC'
            print(nametable)
            cnt5 +=1
            if cnt5 == 21:
                cnt5 = 1
            CNT = cnt5

        elif lll ==6:
            nametable = 'AVIDEO'
            print(nametable)
            cnt6 +=1
            if cnt6 == 21:
                cnt6 = 1
            CNT = cnt6
           
        elif lll ==7:
            nametable = 'AMUSIC'
            print(nametable)
            cnt7 +=1
            if cnt7 == 21:
                cnt7 = 1
            CNT = cnt7

        client_dynamo.put_item(
            TableName=nametable,
            Item = {
                'id' : {
                    'S' : str(CNT)
                    },
                'Mixed' : {
                    'S' : str(round(percent['Mixed'],3))
                    },
                'Negative' : {
                    'S' : str(round(percent['Negative'],3))
                    },
                'Neutral' : {
                    'S' : str(round(percent['Neutral'],3))
                    },
                'Positive' : {
                    'S' : str(round(percent['Positive'],3))
                    },
                'Sentiment' : {
                    'S' : totalSent
                    },
                'Title' : {
                    'S' : title
                    },
                'Vid' : {
                    'S' : vid
                }
            }
        )

    except:
        pass

def main():
    print("***** POSITIVE 영상 *****")
    videosRequest(0, 20,  1) #Positive 영상
    print("***** POSITIVE 음악 *****")
    videosRequest(10, 20,  2) #Positive 음악
    print("***** ALL 영화 *****")
    searchRequest("UC9TorfORDKjpkMTiTJS39Sg", 50, "date", None, 3) #Positive 영화
    print("***** 우울할 때 영상 *****")
    searchRequest(None, 20, "relevance", "우울할 때 보는 영상",  4) #Negative 영상
    print("***** 우울할 때 노래 *****")
    searchRequest(None, 20, "date", "감성 음악",  5) #Negative 노래
    print("***** 화날 때 영상 *****")
    searchRequest(None, 20, "date", "힐링영상",  6) #Negative 영상
    print("***** 화날 때 노래 *****")
    searchRequest(None, 20, "date", "화날 때 듣는 노래", 7) #Negative 노래
    global idle
    idle = 0

if __name__ == '__main__':
#    main() ############  1회용  #################
    while True:        ######## Every 3 days (time loop) ########### 
        day = int(datetime.today().strftime("%d"))
        time = int(datetime.today().strftime("%H%M%S"))
        if day / 3 == 0 and time == 121212:
            main()
        else:
            if idle == 0:
                print('idle!')
                idle = 1
            if keyboard.is_pressed('q'):  ####### press 'q' stop!!
                print('exit!')
                sys.exit()
            elif keyboard.is_pressed('s'):   ##### press 's' update!!
                main()