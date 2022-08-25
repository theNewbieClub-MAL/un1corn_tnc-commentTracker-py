#!/usr/bin/env python3

# cSpell:ignore clearfix dotenv MYANIMELIST

from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
from email.policy import strict
import os
import requests

load_dotenv()

MAL_TO_TRACK = os.environ.get('MYANIMELIST_USERNAME')

r = requests.get("https://myanimelist.net/profile/" + MAL_TO_TRACK)
soup = BeautifulSoup(r.text, features="html.parser")

userComments = soup.find("div", {"class": "user-comments"})
commentAuthor = userComments.find_all("a", {"class": "fw-b"})
commentMessage = userComments.find_all("div", {"class": "comment-text"})

cDict = []
for author, message in zip(commentAuthor, commentMessage):
    comments = {
        'Author': author.text,
        'Content': message.text.strip()
    }
    cDict.append(comments)


def write_csv(items, path):
    # Open the file in write mode
    with open(path, 'w') as f:
        # Return if there's nothing to write
        if len(items) == 0:
            return

        # Write the headers in the first line
        headers = list(items[0].keys())
        f.write('\t'.join(headers) + '\n')

        # Write one item per line
        for item in items:
            values = []
            for header in headers:
                values.append(str(item.get(header, "")))
            f.write('\t'.join(values) + "\n")


write_csv(cDict, "comments.csv")

for i in cDict:
    content = """
**Author**: """ + i['Author'] + """
**Content**: """ + i['Content']
    webhook = DiscordWebhook(url=os.environ.get(
        'DISCORD_WEBHOOK_URI'), rate_limit_retry=True, content=content)
    response = webhook.execute()
