import requests
from datetime import datetime
from pprint import pprint
import ast

def get_all_submissions(username):
    """Get all recent submited problems on github"""

    query="""query getRecentSubmissionList($username: String!) {
            recentSubmissionList(username: $username) {
                title
                titleSlug
                statusDisplay
                timestamp
                lang
            }


        }"""


    variables = {'username':username}
    request = requests.post(" https://leetcode.com/graphql", json={'query': query1,'variables':variables})
    return request.json()

def user_stats_api(username):
    """Get user's submission statistics"""

    query="""query getUserProfile($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        
        matchedUser(username: $username) {
            
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }

            submissionCalendar

            profile {
                ranking
                reputation
                starRating
            }
        }
    }"""

    variables = {'username':username}
    request = requests.post(" https://leetcode.com/graphql", json={'query': query,'variables':variables})
    return request.json()

def get_user_stats(data):
    stats = data['data']['matchedUser']['profile']

    return {'ranking': stats['ranking'],'stars':stats['starRating']}


def get_submissions_difficulty(data):
    difficulties = data['data']['allQuestionsCount']
    submissions = data['data']['matchedUser']['submitStats']['acSubmissionNum']
    results = {}
    for submission, difficulty in zip(submissions,difficulties):
        if submission['difficulty'] == 'All':
            results['solved'] = submission['count']
        else:
            results[submission['difficulty']] = str(submission['count']) +"/"+ str(difficulty['count'])

    return results

def get_submissions_date(username):

    
    query ="""query getRecentSubmissionList($username: String!) {
            matchedUser(username: $username){

                submissionCalendar
                
            }

        }"""

    data = variables = {'username':username}
    request = requests.post(" https://leetcode.com/graphql", json={'query': query,'variables':variables})
    data = request.json()
    submissions = ast.literal_eval(data['data']['matchedUser']['submissionCalendar'])
    results = {}
    for date,count in submissions.items():
        time = datetime.fromtimestamp(int(date)).strftime("%m-%d-%Y")
        results[time] = count

    return results


def get_accepted_submissions(all_submissions):
    """Retrieve accepted submissions and languages"""
    submissions = all_submissions['data']['recentSubmissionList']
    ac_submissions = {}
    for submission in submissions:
        if submission['statusDisplay'] == "Accepted" and submission['title'] not in ac_submissions.keys():
            ac_submissions[submission['title']] = submission['lang']

    return ac_submissions

#print(get_user_stats("tourecheick291"))


#pp = pprint(indent=4)
print(get_submissions_date("tourecheick291"))
#submissions = get_all_submissions("tourecheick291")
#print(get_accepted_submissions(submissions))
#print(get_user_stats("username"))
data = user_stats_api("tourecheick291")
print(get_user_stats(data))
#print(get_submissions_difficulty(data))
#print()
#print(get_submissions_date(data))
#request = requests.post(" https://leetcode.com/graphql",json={'query':query})
#print(request.text)



query="""{
    matchedUser(username: "username") {
        submitStats {
            acSubmissionNum {
                difficulty
                count
                submissions
            }

        }

        submissionCalendar

        profile {
            ranking
            reputation
            starRating
            userAvatar
        }
    }
}"""