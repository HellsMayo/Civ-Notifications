# Civ Notifications

This program parses unread emails sent via webhooks and uses said data to post notifications of new turns within Civilization VI to a discord webhook bot.


This code is designed to function with webhooks sent from Civilization VI for new turns in the Play by Cloud multiplayer mode.

Using https://ifttt.com/, once a webhook is recieved from Civilization, an email is sent to an inbox with the gmail API enabled.

When email_interpreter.py is run, information about player turn, game name, and turn number are parsed from all unread emails of a specific subject (in this case, only emails with the subject "new_turn" will be processed as determined within global_constants.py).

All valid emails have their data stored within a list of dictionaries. This list is then passed to a SendWebhooks object. The object then sends a webhook notifying the appropriate discord user (this is done via their discord id as determined by /note/player\ aliases.csv) within the appropriate text channel for that game (this is done via a discord webhook bot which has their wedhook id and token used for recieving webhooks as determined by /note/game\ aliases.csv)


A file named "credentials.json" is to be stored in the /note directory. This can be downloaded from the second link after pressing "ENABLE GMAIL API" and is specific to the gmail inbox you will be recieveing emails from IFTTT

The required pip installs for this program:
  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
  pip install -U discord.py

Relavant links:
  Play By Cloud - making [Civilization VI] webhook work with Discord
    https://www.reddit.com/r/civ/comments/aqwwui/play_by_cloud_making_webhook_work_with_discord/
  GMail API Quickstart for Python
    https://developers.google.com/gmail/api/quickstart/python
  Create A Discord Webhook With Python For Your Bot
    https://hackaday.com/2018/02/15/creating-a-discord-webhook-in-python/
