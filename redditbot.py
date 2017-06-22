import praw
from config import *
import requests
import traceback
from praw.exceptions import APIException
import logging

# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger = logging.getLogger('prawcore')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)

db_url = 'https://www.doppelbanger.ai/'
db_api_url = 'http://api.doppelbanger.ai:8080/v2/get-matches'
db_api_headers = {
    'User-Agent': 'reddit_bot',
    'content-type': 'image/jpeg,',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'DNT': '1',
}

reply_footer = '''
__________________________________
^^Mention ^^me ^^in ^^any ^^submission ^^linking ^^to ^^an ^^image ^^with ^^a ^^face. ^^| [^^DoppelBanger.ai](https://www.doppelbanger.ai) ^^| [^^bot ^^code](https://github.com/doppelbanger/reddit_bot) 
'''

reply_template = '[I found {} porn stars or cam girls that look like image in OP]({})' + reply_footer
reply_no_matches = 'No matches found for this image. Please see [FAQ](https://www.doppelbanger.ai).' + reply_footer
reply_error = 'Image did not contain a face, too large in size, or not an accepted format. Please see [FAQ](https://www.doppelbanger.ai).' + reply_footer
reply_not_image = 'I only support direct links to JPGs and PNGs at the moment.' + reply_footer
reply_server_error = 'Server seems to be down :('

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     refresh_token=refresh_token,
                     user_agent=user_agent)


def is_image(url):
    # TODO: improve image detection to include common image hosting sites.
    accepted_exts = ['jpg', 'JPG', 'png', 'PNG']
    url = str(url)
    if url.split('.')[-1] in accepted_exts:
        return True
    else:
        return False

replied_threads = []

# 1. check for new mentions
# 2. if parent OP of mention is an image, call doppelbanger api
try:
    for m in reddit.inbox.stream():
        if m.was_comment and '/u/doppelbanger_ai' in m.body:
            c = reddit.comment(m.id)
            s = c.submission
            if s not in replied_threads:
                print('-------')
                print('new mention in new thread')
                replied_threads.append(s)
                if is_image(s.url):
                    print('is image')
                    r = requests.get(s.url)
                    if r.ok:
                        img = r.content
                        # hit doppelbanger api
                        dbr = requests.post(db_api_url, headers=db_api_headers, data=img)
                        if dbr.ok:
                            print('called dbai api')
                            num_actors = len(dbr.json()['matches'])
                            share_url = db_url + dbr.json()['key']
                            if num_actors > 0:
                                reply_text = reply_template.format(num_actors, share_url)
                                c.reply(reply_text)
                                print('replied success')
                                m.mark_read()
                            else:
                                c.reply(reply_no_matches)
                                print('replied no matches')
                                m.mark_read()
                        elif dbr.status_code == 400:
                            print('replied error')
                            c.reply(reply_error)
                            m.mark_read()
                        else:
                            print('replied server down')
                            c.reply(reply_server_error)
                            m.mark_read()
                else:
                    c.reply(reply_not_image)
                    print('replied not image')
                    m.mark_read()
            else:
                m.mark_read()
                print('-------')
                print('old thread')
except APIException:
    traceback.print_exc()
except:
    traceback.print_exc()
