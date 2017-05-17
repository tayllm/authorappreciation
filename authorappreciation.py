import praw

bot = praw.Reddit(user_agent='r/Fantasy Author Appreciation Bot',
                  client_id='MewlbhB1n7oS_Q',
client_secret='sdGRnpD1pn0fCetprM1rNhGc0Rc',
password="&dtT>tSA@b.Z@LYm",
username='RedditFantasyBot')
#client_id='4tRBVBdNzCv2AQ',
#client_secret='JD1B7wOtU3q3m0BmClZ_OkT5148',
#password='hmt2gjt',
#username='LittlePlasticCastle')

authorsPost = "https://www.reddit.com/r/Fantasy/comments/60g42r/author_appreciation_thread_volunteer_thread/"

authorsList = []
authorsEntry = []
#generate the list of author names
submission = bot.submission(url=authorsPost)
lines = submission.selftext.splitlines()

for line in lines:
    if "|" in line:
        entry = line.split("|")
        member = entry[0].strip() 
        author = entry[1].strip()
        if (author.startswith("[")):
            linkStart = author.index("(") + 1
            linkEnd = len(author) 
            link = author[linkStart:linkEnd]
            #link = link.replace(")", "")
            authorEnd = author.index(']') 
            author = author[1:authorEnd]
            valid = [author, link, member]
            print(line)
            print(valid)
            authorsList.append(author)
            authorsEntry.append(valid)
            
        

subreddit = bot.subreddit('grumpkinNsnark')
#subreddit = bot.subreddit('fantasymods')

comments = subreddit.stream.comments()

for comment in comments:
    text = comment.body #Fetch body
    author = comment.author #Fetch author
    for entry in authorsEntry:
        currAuthor = entry[0]
        if currAuthor in text:
            #check to see if the bot has already replied
            #comment.
            
            if 'I am a bot ' not in text:
                currLink = entry[1]
                currMember = entry[2]
                print(entry)
                
                message = "Check out r/Fantasy Author Appreciation post for [" + currAuthor + "](" + currLink + ") from user u/" +  currMember 
                message = message + "\n\n---\n\n ^(I am a bot bleep! bloop! Contact my ~~master~~ creator /u/LittlePlasticCastle with any questions or comments.)"
                    
                comment.reply(message)
                print(message)
  #if ('test' in text.lower()):
   #     message = "A reply to u/{0}".format(author)
#        comment.reply(message)