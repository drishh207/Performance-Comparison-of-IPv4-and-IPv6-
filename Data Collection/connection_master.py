#Script to upload 
from pymongo import MongoClient
from docx import Document

doc = Document('websites_name.docx')

connection_string = "mongodb://localhost:27017/wireless"

# Create a MongoClient instance
client = MongoClient(connection_string)

# Access your MongoDB database
db = client.wireless

# Access a collection within the database
collection = db.master_websites

result = collection.delete_many({})


count = 0
for paragraph in doc.paragraphs:
    count = count + 1
    id = count
    url = paragraph.text    
    document = {"id": id, "url": url}
    result = collection.insert_one(document)
    print(result)




