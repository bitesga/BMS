from pymongo import MongoClient

# Verbindung zur MongoDB-Instanz herstellen
client = MongoClient('localhost', 27017)

# Datenbank und Collections holen
btsDB = client["BTS"]
guilds = btsDB["guilds"]
users = btsDB["users"]

# Guild Metadata

# add new or update Guild Setup
def saveGuild(guild_options):
    guilds.update_one({"guild_id": guild_options["guild_id"]}, {"$set": guild_options}, upsert=True)

# find guild options
def findGuildOptions(guild_id):
    guild_options = guilds.find_one({"guild_id" : guild_id})
    if guild_options:
        return guild_options
    return {"guild_id" : guild_id, "language" : "english"}


# User Options

def saveUser(user_options):
    users.update_one({"discord_id": user_options["discord_id"]}, {"$set": user_options}, upsert=True)

# find guild options
def findUserOptions(discord_id):
    user_options = users.find_one({"discord_id" : discord_id})
    if user_options:
        return user_options
    return {"discord_id" : discord_id, "bs_id" : None, "elo" : 0}

# find guild options
def findUserOptionsByBsId(bs_id):
    user_options = users.find_one({"bs_id" : bs_id})
    if user_options:
        return user_options
    return {"discord_id" : None, "bs_id" : None}
    