import praw
from config import *
import requests
from time import sleep
import traceback
from praw.exceptions import APIException


db_api_url = 'http://www.doppelbanger.ai/v2/get-matches'
db_api_headers = {
    'Origin': 'http://s3-us-west-2.amazonaws.com',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'reddit_bot',
    'content-type': 'image/jpeg,',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'DNT': '1',
}

reply_template = '[I found {} actors that look like image in OP]({})'

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     refresh_token=refresh_token,
                     user_agent=user_agent)


def is_image(url):
    # TODO: improve image detection
    accepted_exts = ['jpg', 'JPG', 'png', 'PNG']
    url = str(url)
    if url.split('.')[-1] in accepted_exts:
        return True
    else:
        return False


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
                        num_actors = len(dbr.json()['matches'])
                        share_url = 'www.doppelbanger.ai/' + dbr.json()['key']
                        if num_actors > 0:
                            reply_text = reply_template.format(num_actors, share_url)
                            c.reply(reply_text)
                            m.mark_read()
                        else:
                            c.reply('No matches found :(')
                            m.mark_read()
                else:
                    c.reply('Not an image.')
                    m.mark_read()
    except APIException:
        traceback.print_exc()
    except:
        traceback.print_exc()

    sleep(30)

