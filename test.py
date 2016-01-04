from pymongo import MongoClient

connection = MongoClient()

db = connection.yelp.places

revcount = 2000


for post in db.find({"review_count" : {"$gt": revcount}}):
        print post

print u'Number of restaurants with {0} reviews: {1}'.format(revcount, db.find({"review_count" : {"$gt": revcount}}).count())