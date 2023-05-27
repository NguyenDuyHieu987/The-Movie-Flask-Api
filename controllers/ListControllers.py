import pymongo
from pymongo.errors import PyMongoError
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage
from flask import *
from pymongo import ReturnDocument
from datetime import datetime
from configs.database import Database
import os
import jwt


class List(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def getlist(self):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )

            skip = request.args.get("skip", default=0, type=int)
            if skip == 0:
                list = self.__db["lists"].find_one(
                    {"id": jwtUser["id"]}, {"items": {"$slice": [skip * 20, 20]}}
                )

                total = self.__db["lists"].aggregate(
                    [
                        {"$match": {"id": str(jwtUser["id"])}},
                        {
                            "$project": {
                                "total": {"$size": "$items"},
                                #   "result": "$items"
                            }
                        },
                    ]
                )
                # total = self.__db["lists"].find_one({"id": jwtUser["id"]})

                return {"result": cvtJson(list), "total": cvtJson(total)[0]["total"]}

            elif skip > 0:
                list = self.__db["lists"].find_one(
                    {"id": jwtUser["id"]}, {"items": {"$slice": [skip * 20, 20]}}
                )

                return {"result": cvtJson(list["items"]), "total": len(list["items"])}

        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"success": False, "result": "Failed to get list"}

    def search_list(self):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )
            # skip = request.args.get("skip", default=0, type=int)
            query = request.args.get("query", default="", type=str)

            if len(query) != 0:
                list = self.__db["lists"].find_one(
                    {"id": jwtUser["id"]},
                    {
                        "items": {
                            "$elemMatch": {
                                "$or": [
                                    {"name": {"$regex": query, "$options": "i"}},
                                    {
                                        "original_name": {
                                            "$regex": query,
                                            "$options": "i",
                                        }
                                    },
                                ],
                            },
                        }
                    },
                )

                if "items" in list:
                    return {
                        "results": cvtJson(list["items"]),
                        "total": len(list["items"]),
                    }
                else:
                    return {"results": [], "total": 0}

            else:
                list = self.__db["lists"].find_one({"id": jwtUser["id"]})
                total = self.__db["lists"].aggregate(
                    [
                        {"$match": {"id": str(jwtUser["id"])}},
                        {
                            "$project": {
                                "total": {"$size": "$items"},
                                #   "result": "$items"
                            }
                        },
                    ]
                )
                return {
                    "results": cvtJson(list["items"]),
                    "total": cvtJson(total)[0]["total"],
                }
        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"success": False, "result": "Failed to search list"}

    def getitem_list(self, idmovie):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )
            item_lists = self.__db["lists"].find_one(
                {"id": jwtUser["id"]}, {"items": {"$elemMatch": {"id": int(idmovie)}}}
            )
            if "items" in item_lists:
                return {"success": True, "result": cvtJson(item_lists["items"][0])}
            else:
                return {"success": False, "result": "Failed to get item in list"}

        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"success": False, "result": "Failed to get item in list"}

    def additem_list(self):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )

            media_type = request.form["media_type"]
            media_id = request.form["media_id"]

            if media_type == "movie":
                movie = self.__db["movies"].find_one(
                    {"id": int(media_id)},
                    {
                        "images": 0,
                        "credits": 0,
                        "videos": 0,
                        "production_companies": 0,
                    },
                )

                if movie != None:
                    item_lists = self.__db["lists"].find_one(
                        {"id": jwtUser["id"]},
                        {"items": {"$elemMatch": {"id": int(media_id)}}},
                    )
                    if "items" in item_lists:
                        return {
                            "success": False,
                            "exist": True,
                            "result": "Movie already exist in list",
                        }
                    else:
                        self.__db["lists"].find_one_and_update(
                            {"id": jwtUser["id"]},
                            {
                                # "$addToSet": {
                                "$push": {
                                    "items": {
                                        "$each": [
                                            {
                                                "id": int(media_id),
                                                "name": movie["name"],
                                                "original_name": movie["original_name"],
                                                "original_language": movie[
                                                    "original_language"
                                                ],
                                                "media_type": media_type,
                                                "genres": movie["genres"],
                                                "backdrop_path": movie["backdrop_path"],
                                                "poster_path": movie["poster_path"],
                                                "dominant_backdrop_color": movie[
                                                    "dominant_backdrop_color"
                                                ],
                                                "dominant_poster_color": movie[
                                                    "dominant_poster_color"
                                                ],
                                                "created_at": str(datetime.now()),
                                                "updated_at": str(datetime.now()),
                                            }
                                        ],
                                        "$position": 0,
                                    }
                                }
                            },
                            {"new": True},
                            upsert=True,
                            return_document=ReturnDocument.AFTER,
                        )
                        return {
                            "success": True,
                            "results": "Add item to list suucessfully",
                        }
                else:
                    return {
                        "success": False,
                        "results": "Failed to add item to list",
                    }

            elif media_type == "tv":
                tv = self.__db["tvs"].find_one(
                    {"id": int(media_id)},
                    {
                        "images": 0,
                        "credits": 0,
                        "videos": 0,
                        "production_companies": 0,
                        "seasons": 0,
                    },
                )
                if tv != None:
                    item_lists = self.__db["lists"].find_one(
                        {"id": jwtUser["id"]},
                        {"items": {"$elemMatch": {"id": int(media_id)}}},
                    )
                    if "items" in item_lists:
                        return {
                            "success": False,
                            "exist": True,
                            "result": "Tv already exist in list",
                        }
                    else:
                        self.__db["lists"].find_one_and_update(
                            {"id": jwtUser["id"]},
                            {
                                # "$addToSet": {
                                "$push": {
                                    "items": {
                                        "$each": [
                                            {
                                                "id": int(media_id),
                                                "name": tv["name"],
                                                "original_name": tv["original_name"],
                                                "original_language": tv[
                                                    "original_language"
                                                ],
                                                "media_type": media_type,
                                                "genres": tv["genres"],
                                                "backdrop_path": tv["backdrop_path"],
                                                "poster_path": tv["poster_path"],
                                                "dominant_backdrop_color": tv[
                                                    "dominant_backdrop_color"
                                                ],
                                                "dominant_poster_color": tv[
                                                    "dominant_poster_color"
                                                ],
                                                "created_at": str(datetime.now()),
                                                "updated_at": str(datetime.now()),
                                            }
                                        ],
                                        "$position": 0,
                                    }
                                }
                            },
                            {"new": True},
                            upsert=True,
                            return_document=ReturnDocument.AFTER,
                        )
                        return {
                            "success": True,
                            "results": "Add item to list suucessfully",
                        }
                else:
                    return {
                        "success": False,
                        "results": "Failed to add item to list",
                    }
        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {
                "success": False,
                "results": "Failed to add item to list",
            }

    def remove_item_list(self):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )

            media_id = request.form["media_id"]

            self.__db["lists"].find_one_and_update(
                {"id": jwtUser["id"]},
                {"$pull": {"items": {"id": int(media_id)}}},
                {"new": True},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            list = cvtJson(self.__db["lists"].find_one({"id": jwtUser["id"]}))

            return {"success": True, "results": list["items"]}
        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"success": False, "result": "Failed to remove item from list"}

    def removeall_item_list(self):
        try:
            user_token = request.headers["Authorization"].replace("Bearer ", "")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_TOKEN_SECRET")),
                algorithms=["HS256"],
            )

            self.__db["lists"].find_one_and_update(
                {"id": jwtUser["id"]},
                {"$set": {"items": []}},
                {"new": True},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            list = cvtJson(self.__db["lists"].find_one({"id": jwtUser["id"]}))

            return {"success": True, "results": list["items"]}

        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"success": False, "result": "Failed to remove all item from list"}
