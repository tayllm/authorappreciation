import praw
import os
import psycopg2
from pymongo import MongoClient
import urllib

#client = MongoClient('mongodb://heroku_8pzzctpn:hnnu9ch1h6j867d2eiq613bbnl@ds149201.mlab.com:49201/heroku_8pzzctpn?retryWrites=false')
mongo_uri = "mongodb+srv://heroku_8pzzctpn:wWC54yhe5uEKEQDZ@cluster-8pzzctpn.0a7uv.mongodb.net/heroku_8pzzctpn?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
#client = MongoClient('mongodb+srv://heroku_8pzzctpn:k@DZdbdSWd3BYCs@cluster-8pzzctpn.0a7uv.mongodb.net/heroku_8pzzctpn?retryWrites=true&w=majority')
db = client.get_default_database()

#urlparse.uses_netloc.append("postgres")
#url = urlparse.urlparse(os.environ["DATABASE_URL"])

#conn = psycopg2.connect(
#    database=url.path[1:],
#    user=url.username,
#    password=url.password,
#    host=url.hostname,
#    port=url.port
#)

# mongodb://heroku_8pzzctpn:hnnu9ch1h6j867d2eiq613bbnl@ds149201.mlab.com:49201/heroku_8pzzctpn

is_prod = os.getenv("IS_HEROKU")
#print(is_prod)
dev = os.getenv("IS_TEST")
if dev == 'TRUE':
    c_id=os.environ['AUTHOR_CLIENT_ID_TEST']
    c_secret=os.environ['AUTHOR_CLIENT_SECRET_TEST']
    pw= os.environ['REDDIT_PASSWORD_TEST']
    u= os.environ['REDDIT_USERNAME_TEST']
    sub= os.environ['SUBREDDIT_TEST']
else:
    c_id=os.environ['AUTHOR_CLIENT_ID']
    c_secret=os.environ['AUTHOR_CLIENT_SECRET']
    pw= os.environ['REDDIT_PASSWORD']
    u= os.environ['REDDIT_USERNAME']
    sub= os.environ['SUBREDDIT']

print(sub)

if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
       posts_replied_to = f.read()
       posts_replied_to = posts_replied_to.split("\n")
       posts_replied_to = list(filter(None, posts_replied_to))

print(u)

bot = praw.Reddit(user_agent='r/Fantasy Author Appreciation Bot',
                  client_id=c_id,
client_secret=c_secret,
password=pw,
username=u)


authorsWiki = "https://www.reddit.com/r/Fantasy/wiki/authorappreciation"
optoutWiki = "https://www.reddit.com/r/FantasyMods/wiki/opt-out"
modWiki = bot.subreddit('fantasymods').wiki['opt-out'].content_md
optoutList = modWiki.splitlines()

authorsList = []
authorsEntry = []
#generate the list of author names
submission = bot.subreddit('fantasy').wiki['authorappreciation'].content_md #bot.submission(url=authorsWiki)
lines = submission.splitlines()

numReplies=0

for line in lines:
    if "|" in line:
        entry = line.split("|")
        member = entry[0].strip() 
        author = entry[1].strip()
        if (author.startswith("[")):
            linkStart = author.index("(") + 1
            linkEnd = author.index(")")  #len(author) - 1
            link = author[linkStart:linkEnd].strip()
            #link = link.replace(")", "")
            authorEnd = author.index(']') 
            author = author[1:authorEnd].strip()
            valid = [author, link, member]
            #print(line)
            #print(valid)
            authorsList.append(author)
            authorsEntry.append(valid)
            
#only execute if it is limited to a subreddit        
if (sub):
    subreddit = bot.subreddit(sub)
    #comments = subreddit.stream.comments()
    comments = subreddit.comments(limit=250)
    processed = list()
    for comment in comments:
        # There seem to be duplicate responses from the bot occassionaly, within seconds, so posted
        # with the same run of authorappreciationbot.
        # Make sure to handle if duplicate comment ids are returned from praw
        # Only process 1, skip others. If this keeps happening, will revisit
        if comment.id not in processed:
            processed.append(comment.id)
            replied = db['replied']

            new_reply = {'replied':comment.id}
            
            # Check if the bot has already replied to this comment
            if not db.author_appreciation.find_one(new_reply):
                text = comment.body #Fetch body
                author = comment.author #Fetch author

                #Check for Opt Out Comment
                if text.lower() == '!optout' :
                    parentcomment = bot.comment(comment.parent_id)

                    if parentcomment.author == 'RedditFantasyBot':
                        bot.subreddit('fantasymods').wiki['opt-out'].edit(content=modWiki + "\n" + author.name)
                        result = db.author_appreciation.insert_one(new_reply)

                # Check if this comment is opting out of the bot
                if '!noauthorbot' not in text:
                    # Verify the author of the comment has not opted out of all bot replies
                    if author not in optoutList:

                        includeAuthors = ""
                        for entry in authorsEntry:
                            currAuthor = entry[0]
                            if currAuthor == "Avi":
                                currAuthor = " Avi "

                            if currAuthor in text:
                                # Make sure this is not a bot comment
                                if 'I am a bot ' not in text:
                                    currLink = entry[1].strip()
                                    currMember = entry[2]
                                    print(entry)
                                    #includeAuthors = includeAuthors + "* [Author Appreciation post for **" + currAuthor + "**](" + currLink + ") from user u /" +  currMember + " \n"
                                    #find the subject for the original post
                                    aaPost = bot.submission(url=currLink)
                                    title = aaPost.title
                                    if currAuthor in title:
                                        title = title.replace(currAuthor, "**" + currAuthor + "**")
                                    else:
                                        title = "**" + currAuthor + "**: " + title
                                    includeAuthors = includeAuthors + "* [" + title + "](" + currLink + ") from user u/" +  currMember + " \n"
                        if (includeAuthors):       
                            message = "r/Fantasy's [Author Appreciation series](" + authorsWiki + ") has posts for an author you mentioned  \n\n"
                            message = message + includeAuthors
                            message = message + "\n\n---\n\n ^(I am a bot bleep! bloop! Contact my ~~master~~ creator /u/LittlePlasticCastle with any questions or comments.)"
                            message = message + "\n\n^(To prevent a reply for a single post, include the text '!noauthorbot'.  To opt out of the bot for all your future posts, reply with '!optout'.)"

                            #Make the reply and add id to the db to avoid duplicate replies            
                            comment.reply(message)
                            result = db.author_appreciation.insert_one(new_reply)
                            numReplies = numReplies + 1
                            #posts_replied_to.append(comment.id)
                            #with open("posts_replied_to.txt", "a") as f:
                            #    f.write(comment.id + "\n")
                            print(message)
        
client.close()
print ("Number of comment replies: ")
print(numReplies)

        #if ('test' in text.lower()):
        #     message = "A reply to u/{0}".format(author)
        #        comment.reply(message)
