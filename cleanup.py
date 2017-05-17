import praw

bot = praw.Reddit(user_agent='r/Fantasy Author Appreciation Bot',
                  client_id='4tRBVBdNzCv2AQ',
client_secret='JD1B7wOtU3q3m0BmClZ_OkT5148',
password='hmt2gjt',
username='littleplasticcastle')

authorsPost = "https://www.reddit.com/r/grumpkinNsnark/comments/6bj78l/test/"

        

subreddit = bot.subreddit('grumpkinNsnark')

comments = subreddit.stream.comments()

for comment in comments:
    print(comment.body)
    comment.delete()
    