import motor.motor_asyncio

async def connect_to_mongodb():
    mongo_uri = "mongodb://localhost:27017"  # Замените это на вашу URI MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    return client

async def get_collection(database_name, collection_name):
    client = await connect_to_mongodb()
    database = client[database_name]
    collection = database[collection_name]
    return collection

async def insert_data(collection, data):
    result = await collection.insert_one(data)
    return result

async def check_duplicate_data(collection, data):
    existing_data = await collection.find_one(data)
    return existing_data is not None

async def update_one_document(collection, filter, update):
    result = await collection.update_one(filter, {"$set": update})
    return result.modified_count > 0

async def find_one_document(collection, date):
    document = await collection.find_one(date)
    return document

async def get_top_users(users_collection, limit=5):
    top_users_cursor = users_collection.find().sort("balance", -1).limit(limit)
    top_users = []
    async for user in top_users_cursor:
        top_users.append(user)
    return top_users


