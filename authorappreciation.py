import praw
import os
import psycopg2
from pymongo import MongoClient

#client = MongoClient('mongodb://heroku_8pzzctpn:hnnu9ch1h6j867d2eiq613bbnl@ds149201.mlab.com:49201/heroku_8pzzctpn?retryWrites=false')
client = MongoClient('mongodb+srv://heroku_8pzzctpn:k@DZdbdSWd3BYCs@cluster-8pzzctpn.0a7uv.mongodb.net/heroku_8pzzctpn?retryWrites=true&w=majority')
db = client.get_default_database()


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
print(is_prod)
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
    #subreddit = bot.subreddit('fantasymods')

    #comments = subreddit.stream.comments()
    comments = subreddit.comments(limit=250)

    for comment in comments:
        replied = db['replied']

        new_reply = {'replied':comment.id}
        if not db.author_appreciation.find_one(new_reply):
       # if comment.id not in posts_replied_to:
            text = comment.body #Fetch body
            author = comment.author #Fetch author
            includeAuthors = ""
            for entry in authorsEntry:
                currAuthor = entry[0]
                if currAuthor == "Avi":
                    currAuthor = " Avi "

                if currAuthor in text:
                    #check to see if the bot has already replied
                    #comment.
                    
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

                #Make the reply and add id to the db to avoid duplicate replies            
                comment.reply(message)
                result = db.author_appreciation.insert_one(new_reply)
                numReplies = numReplies + 1
                #posts_replied_to.append(comment.id)
                #with open("posts_replied_to.txt", "a") as f:
                #    f.write(comment.id + "\n")
                print(message)

client.close()
print (numReplies)

        #if ('test' in text.lower()):
        #     message = "A reply to u/{0}".format(author)
        #        comment.reply(message)
