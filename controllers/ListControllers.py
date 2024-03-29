import pymongo
from pymongo.errors import PyMongoError
from flask import *
from pymongo import ReturnDocument
from datetime import datetime
from configs.database import Database
import os
import jwt
import uuid
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage, InternalServerErrorMessage
from utils.exceptions import DefaultError


class List(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def get_all(self, type):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            skip = request.args.get("skip", default=1, type=int) - 1
            limit = request.args.get("limit", default=20, type=int)

            if type == "all":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                        }
                    )
                    .skip(skip * limit)
                    .limit(limit)
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                total = self.__db["lists"].count_documents(
                    {
                        "user_id": jwtUser["id"],
                    }
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": total,
                }

            elif type == "movie":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                            "media_type": type,
                        },
                    )
                    .skip(skip * limit)
                    .limit(limit)
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                total = self.__db["lists"].count_documents(
                    {
                        "user_id": jwtUser["id"],
                        "media_type": type,
                    },
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": total,
                }

            elif type == "tv":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                            "media_type": type,
                        },
                    )
                    .skip(skip * limit)
                    .limit(limit)
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                total = self.__db["lists"].count_documents(
                    {
                        "user_id": jwtUser["id"],
                        "media_type": type,
                    },
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": total,
                }

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def search(self, type):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            # skip = request.args.get("skip", default=0, type=int)
            query = request.args.get("query", default="", type=str)

            if type == "all":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                            "$or": [
                                {"name": {"$regex": query, "$options": "i"}},
                                {"original_name": {"$regex": query, "$options": "i"}},
                            ],
                        }
                    )
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": len(cvtJson(list)) if list != None else 0,
                }

            elif type == "movie":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                            "media_type": type,
                            "$or": [
                                {"name": {"$regex": query, "$options": "i"}},
                                {"original_name": {"$regex": query, "$options": "i"}},
                            ],
                        },
                    )
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": len(cvtJson(list)) if list != None else 0,
                }

            elif type == "tv":
                list = (
                    self.__db["lists"]
                    .find(
                        {
                            "user_id": jwtUser["id"],
                            "media_type": type,
                            "$or": [
                                {"name": {"$regex": query, "$options": "i"}},
                                {"original_name": {"$regex": query, "$options": "i"}},
                            ],
                        },
                    )
                    .sort(
                        [("created_at", pymongo.DESCENDING)],
                    )
                )

                return {
                    "results": cvtJson(list) if list != None else [],
                    "total": len(cvtJson(list)) if list != None else 0,
                }

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def get(self, type, movieId):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            item_list = self.__db["lists"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "movie_id": movieId,
                    "media_type": type,
                },
            )

            if item_list != None:
                return {"success": True, "result": cvtJson(item_list)}
            else:
                return {
                    "success": False,
                    "result": "This movie is not found in your list",
                }

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def add(self):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            movie_id = request.form.get("movie_id")
            media_type = request.form.get("media_type")
            id_list = str(uuid.uuid4())

            if media_type == "movie":
                movie = self.__db["movies"].find_one(
                    {"id": movie_id},
                )

                if movie != None:
                    item_lists = self.__db["lists"].find_one(
                        {
                            "user_id": jwtUser["id"],
                            "movie_id": movie_id,
                            "media_type": media_type,
                        },
                    )

                    if item_lists == None:
                        self.__db["lists"].insert_one(
                            {
                                "id": str(id_list),
                                "user_id": jwtUser["id"],
                                "movie_id": movie_id,
                                "name": movie["name"],
                                "original_name": movie["original_name"],
                                "original_language": movie["original_language"],
                                "media_type": media_type,
                                "genres": movie["genres"],
                                "backdrop_path": movie["backdrop_path"],
                                "poster_path": movie["poster_path"],
                                "dominant_backdrop_color": movie[
                                    "dominant_backdrop_color"
                                ],
                                "dominant_poster_color": movie["dominant_poster_color"],
                                "created_at": datetime.now(),
                                "updated_at": datetime.now(),
                            }
                        )

                        return {
                            "success": True,
                            "results": "Add item to list suucessfully",
                        }
                    else:
                        raise DefaultError("Movie is already exist in list")

                else:
                    raise DefaultError("Movie is not exists")

            elif media_type == "tv":
                tv = self.__db["tvs"].find_one(
                    {"id": movie_id},
                )

                if tv != None:
                    item_lists = self.__db["lists"].find_one(
                        {
                            "user_id": jwtUser["id"],
                            "movie_id": movie_id,
                            "media_type": media_type,
                        },
                    )

                    if item_lists != None:
                        raise DefaultError("Movie already exist in list")
                    else:
                        self.__db["lists"].insert_one(
                            {
                                "id": str(id_list),
                                "user_id": jwtUser["id"],
                                "movie_id": movie_id,
                                "name": tv["name"],
                                "original_name": tv["original_name"],
                                "original_language": tv["original_language"],
                                "media_type": media_type,
                                "genres": tv["genres"],
                                "backdrop_path": tv["backdrop_path"],
                                "poster_path": tv["poster_path"],
                                "dominant_backdrop_color": tv[
                                    "dominant_backdrop_color"
                                ],
                                "dominant_poster_color": tv["dominant_poster_color"],
                                "created_at": datetime.now(),
                                "updated_at": datetime.now(),
                            }
                        )

                        return {
                            "success": True,
                            "results": "Add item to list suucessfully",
                        }
                else:
                    raise DefaultError("Movie is not exists")

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except DefaultError as e:
            BadRequestMessage(e.message)
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def remove(self):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            id = request.form.get("id")
            movie_id = request.form.get("movie_id")
            media_type = request.form.get("media_type")

            resultDelete1 = self.__db["lists"].delete_one(
                {
                    "user_id": jwtUser["id"],
                    "movie_id": movie_id,
                    "media_type": media_type,
                },
            )

            if resultDelete1.deleted_count == 1:
                return {
                    "success": True,
                    "results": "Remove item from list suucessfully",
                }
            else:
                raise DefaultError("Delete movie from list failed")

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except DefaultError as e:
            BadRequestMessage(e.message)
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def clear(self):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            resultDelete = self.__db["lists"].delete_many(
                {"user_id": jwtUser["id"]},
            )

            if resultDelete.deleted_count >= 1:
                list = (
                    self.__db["lists"].find({"user_id": jwtUser["id"]}).skip(0).limit(1)
                )
                return {"success": True, "results": cvtJson(list)}
            else:
                raise DefaultError("Delete all movie from list failed")

        except jwt.ExpiredSignatureError as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is expired")
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError) as e:
            make_response().delete_cookie(
                "user_token", samesite="lax", secure=True, httponly=False
            )
            InternalServerErrorMessage("Token is invalid")
        except DefaultError as e:
            BadRequestMessage(e.message)
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)
