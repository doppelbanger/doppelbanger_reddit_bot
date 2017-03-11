import praw
from secrets import *


reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     redirect_uri=redirect_uri)

scopes = ['edit', 'privatemessages', 'history',
          'save', 'identity', 'submit', 'read']

print(reddit.auth.url(scopes, 'dg', 'permanent'))
# go to url, and authenticate to get "CODE"
print(reddit.auth.authorize(code))
# get the refresh_token


for m in reddit.inbox.mentions(limit=50):
    if m.new:
        c = reddit.comment(m.id)
        s = c.submission
        # if s.url is an image:
        #     hit doppelgangsta api
        #     if response is good:
        #         c.reply()
