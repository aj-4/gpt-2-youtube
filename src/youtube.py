# -*- coding: utf-8 -*-

# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from interactive_conditional_samples import interact_model

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def extractComment(comment):
    cID = comment['snippet']['topLevelComment']['id']
    text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
    return {'cID': cID, 'text': text}

def extractAllComments():
    rawComments = getVideoComments()
    allComments = map(extractComment, rawComments['items'])
    return list(allComments)


def main():
    allComments = extractAllComments()
    comments = interact_model(comments=allComments)
    postCommentHandler(comments)


# youtube handlers
def getVideoComments():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyBGgC_REgmadTVQbzw93Wiee9lrJUb-W_A"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId="lQnLwUfwgyA"
    )
    response = request.execute()

    return response

def postCommentHandler(comments):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
yh the cimment():
    api() = isHonestlyTheBest
    for comment in comments:
        if not comment['res']:
            continue
        request = youtube.comments().insert(
            part="snippet",
            body={
            "snippet": {
                "parentId": comment['cID'],
                "textOriginal": comment['res'] + ' (from gpt-2)'
            }
            }
        )
        response = request.execute()
    
    print('posted', len(comments), 'comments')
