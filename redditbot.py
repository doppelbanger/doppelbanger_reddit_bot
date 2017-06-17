import praw
from config import *
import requests
from time import sleep
import traceback
from praw.exceptions import APIException
import logging

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('prawcore')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

db_url = 'https://www.doppelbanger.ai/'
db_api_url = '35.167.92.242:8080/v2/get-matches'
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
reply_no_matches = 'No matches found for this image. Please see [FAQ](https://www.doppelbanger.ai#faq).' + reply_footer
reply_error = 'Image did not contain a face, too large in size, or not an accepted format. Please see [FAQ](https://www.doppelbanger.ai#faq).' + reply_footer
reply_not_image = 'I only support direct links to JPGs and PNGs at the moment.' + reply_footer

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


# Every 30 seconds:
# 1. check for new mentions
# 2. if parent OP of mention is an image, call doppelbanger api
while True:
    try:
        for m in reddit.inbox.mentions(limit=50):
            if m.new:
                c = reddit.comment(m.id)
                s = c.submission
                if is_image(s.url):
                    r = requests.get(s.url)
                    if r.ok:
                        img = r.content
                        # hit doppelbanger api
                        dbr = requests.post(db_api_url, headers=db_api_headers, data=img)
                        if dbr.ok:
                            num_actors = len(dbr.json()['matches'])
                            share_url = db_url + dbr.json()['key']
                            if num_actors > 0:
                                reply_text = reply_template.format(num_actors, share_url)
                                c.reply(reply_text)
                                m.mark_read()
                            else:
                                c.reply(reply_no_matches)
                                m.mark_read()
                        elif r.status_code == 400:
                            c.reply(reply_error)
                            m.mark_read()
                else:
                    c.reply(reply_not_image)
                    m.mark_read()
    except APIException:
        traceback.print_exc()
    except:
        traceback.print_exc()

    sleep(30)
