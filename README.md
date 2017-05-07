# doppelbanger_reddit_

## create config.py
1. `cp config_example.py config.py`
2. Create a new app here: https://www.reddit.com/prefs/apps/
3. Get the app's `client_id` and `client_secret`

## generate secrets.py

```
import praw

scopes = ['edit', 'privatemessages', 'history',
          'save', 'identity', 'submit', 'read']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     redirect_uri=redirect_uri)
print(reddit.auth.url(scopes, user_agent, 'permanent'))
```
go to url, and authenticate to get "CODE"
```
print(reddit.auth.authorize(code))
```
get the `refresh_token`