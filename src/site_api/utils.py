import os
import random
import string

from bson import ObjectId
from fastapi import Response
from gridfs import GridFS
from pymongo import MongoClient


def generate_invite_code():
    """Generate a team invite code."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


def create_client():
    uri = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@tripsync-mongo"
    return MongoClient(uri)


def upload_profile_picture(username, image):
    client = create_client()

    db = client["pfps"]
    fs = GridFS(db)

    file_id = fs.put(image.file, filename=image.filename)

    user_to_pfp = {"user": username, "image_id": file_id}
    utp_collection = db["user_to_pfp"]
    utp_collection.insert_one(user_to_pfp)

    client.close()

    return {"message": "Profile picture uploaded!"}


def retrieve_pfp(username):
    client = create_client()

    db = client["pfps"]
    fs = GridFS(db)
    user_to_pfp = db["user_to_pfp"]
    documents = user_to_pfp.find({"user": username}).sort("_id", -1).limit(1)
    document = next(documents, None)
    if document:
        image_id = document["image_id"]
        grid_out = fs.get(ObjectId(image_id))
        return Response(content=grid_out.read(), media_type="image/jpeg")
    else:
        return Response(content=b"", media_type="image/jpeg")


def upload_thumbnail_image(vacation, image):
    client = create_client()

    db = client["thumbnails"]
    fs = GridFS(db)

    file_id = fs.put(image.file, filename=image.filename)

    vacation_to_thumbnail = {"vacation": vacation, "image_id": file_id}
    vtt_collection = db["vacation_to_thumbnail"]
    vtt_collection.insert_one(vacation_to_thumbnail)

    client.close()

    return {"message": "Thumbnail uploaded!"}


def retrieve_thumbnail(vacation):
    client = create_client()

    db = client["thumbnails"]
    fs = GridFS(db)
    vacation_to_thumbnail = db["vacation_to_thumbnail"]
    documents = (
        vacation_to_thumbnail.find({"vacation": vacation}).sort("_id", -1).limit(1)
    )
    document = next(documents, None)
    if document:
        image_id = document["image_id"]
        grid_out = fs.get(ObjectId(image_id))
        return Response(content=grid_out.read(), media_type="image/jpeg")
    else:
        return Response(content=b"", media_type="image/jpeg")
