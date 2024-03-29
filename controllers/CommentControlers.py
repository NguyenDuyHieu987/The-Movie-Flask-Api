import pymongo
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from flask import *
from configs.database import Database
import uuid
import os
import jwt
from datetime import datetime
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage, InternalServerErrorMessage
from utils.exceptions import DefaultError, NotInTypeError


class Comment(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def get_all_parent(self, movieType, movieId):
        try:
            skip = request.args.get("skip", default=1, type=int) - 1
            limit = request.args.get("limit", default=20, type=int)

            # comments = (
            #     self.__db["comments"]
            #     .find(
            #         {
            #             "movie_id": str(movieId),
            #             "movie_type": str(movieType),
            #             "type": "parent",
            #         }
            #     )
            #     .sort(
            #         [("created_at", pymongo.DESCENDING)],
            #     )
            #     .skip(skip * limit)
            #     .limit(limit)
            # )

            headers = request.headers

            likeDislike = []

            if "Authorization" in headers or request.cookies.get("user_token") != None:
                user_token = request.headers["Authorization"].replace(
                    "Bearer ", ""
                ) or request.cookies.get("user_token")

                jwtUser = jwt.decode(
                    user_token,
                    str(os.getenv("JWT_SIGNATURE_SECRET")),
                    algorithms=["HS256"],
                )

                likeDislike = [
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {
                                    "$match": {
                                        "$and": [
                                            {"$expr": {"$eq": ["$type", "like"]}},
                                            {
                                                "$expr": {
                                                    "$eq": ["$user_id", jwtUser["id"]]
                                                }
                                            },
                                        ],
                                    },
                                },
                            ],
                            "as": "is_like",
                        },
                    },
                    {
                        "$addFields": {
                            "is_like": {
                                "$eq": [{"$size": "$is_like"}, 1],
                            },
                        },
                    },
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {
                                    "$match": {
                                        "$and": [
                                            {"$expr": {"$eq": ["$type", "dislike"]}},
                                            {
                                                "$expr": {
                                                    "$eq": ["$user_id", jwtUser["id"]]
                                                }
                                            },
                                        ],
                                    },
                                },
                            ],
                            "as": "is_dislike",
                        },
                    },
                    {
                        "$addFields": {
                            "is_dislike": {
                                "$eq": [{"$size": "$is_dislike"}, 1],
                            },
                        },
                    },
                ]

            comments = self.__db["comments"].aggregate(
                [
                    {
                        "$match": {
                            "movie_id": str(movieId),
                            "movie_type": str(movieType),
                            "type": "parent",
                        }
                    },
                    {"$skip": skip * limit},
                    {"$limit": limit},
                    {
                        "$lookup": {
                            "from": "comments",
                            "localField": "id",
                            "foreignField": "parent_id",
                            "as": "childrens",
                        }
                    },
                    {
                        "$addFields": {
                            "childrens": {"$size": "$childrens"},
                        },
                    },
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$type", "like"]}}}
                            ],
                            "as": "like",
                        }
                    },
                    {
                        "$addFields": {
                            "like": {"$size": "$like"},
                        },
                    },
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$type", "dislike"]}}}
                            ],
                            "as": "dislike",
                        }
                    },
                    {
                        "$addFields": {
                            "dislike": {"$size": "$dislike"},
                        },
                    },
                    {
                        "$sort": {
                            "created_at": pymongo.DESCENDING,
                            # "like": pymongo.DESCENDING,
                            # "dislike": pymongo.DESCENDING
                        }
                    },
                    *likeDislike,
                ]
            )

            total = self.__db["comments"].count_documents(
                {
                    "movie_id": str(movieId),
                    "movie_type": str(movieType),
                }
            )

            return {"results": cvtJson(comments), "total": total}
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def get_child(self, movieType, movieId, parentId):
        try:
            skip = request.args.get("skip", default=1, type=int) - 1
            limit = request.args.get("limit", default=10, type=int)

            # comments = (
            #     self.__db["comments"]
            #     .find(
            #         {
            #             "movie_id": str(movieId),
            #             "parent_id": str(parentId),
            #             "movie_type": str(movieType),
            #             "type": "children",
            #         }
            #     )
            #     .sort(
            #         [("created_at", pymongo.ASCENDING)],
            #     )
            #     .skip(skip * limit)
            #     .limit(limit)
            # )

            headers = request.headers

            likeDislike = []

            if "Authorization" in headers or request.cookies.get("user_token") != None:
                user_token = request.headers["Authorization"].replace(
                    "Bearer ", ""
                ) or request.cookies.get("user_token")

                jwtUser = jwt.decode(
                    user_token,
                    str(os.getenv("JWT_SIGNATURE_SECRET")),
                    algorithms=["HS256"],
                )

                likeDislike = [
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {
                                    "$match": {
                                        "$and": [
                                            {"$expr": {"$eq": ["$type", "like"]}},
                                            {
                                                "$expr": {
                                                    "$eq": ["$user_id", jwtUser["id"]]
                                                }
                                            },
                                        ],
                                    },
                                },
                            ],
                            "as": "is_like",
                        },
                    },
                    {
                        "$addFields": {
                            "is_like": {
                                "$eq": [{"$size": "$is_like"}, 1],
                            },
                        },
                    },
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {
                                    "$match": {
                                        "$and": [
                                            {"$expr": {"$eq": ["$type", "dislike"]}},
                                            {
                                                "$expr": {
                                                    "$eq": ["$user_id", jwtUser["id"]]
                                                }
                                            },
                                        ],
                                    },
                                },
                            ],
                            "as": "is_dislike",
                        },
                    },
                    {
                        "$addFields": {
                            "is_dislike": {
                                "$eq": [{"$size": "$is_dislike"}, 1],
                            },
                        },
                    },
                ]

            comments = self.__db["comments"].aggregate(
                [
                    {
                        "$match": {
                            "movie_id": str(movieId),
                            "parent_id": str(parentId),
                            "movie_type": str(movieType),
                            "type": "children",
                        }
                    },
                    {"$skip": skip * limit},
                    {"$limit": limit},
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$type", "like"]}}}
                            ],
                            "as": "like",
                        }
                    },
                    {
                        "$addFields": {
                            "like": {"$size": "$like"},
                        },
                    },
                    {
                        "$lookup": {
                            "from": "commentlikes",
                            "localField": "id",
                            "foreignField": "comment_id",
                            "pipeline": [
                                {"$match": {"$expr": {"$eq": ["$type", "dislike"]}}}
                            ],
                            "as": "dislike",
                        }
                    },
                    {
                        "$addFields": {
                            "dislike": {"$size": "$dislike"},
                        },
                    },
                    {
                        "$sort": {
                            "created_at": pymongo.ASCENDING,
                            # "like": pymongo.DESCENDING,
                            # "dislike": pymongo.DESCENDING
                        }
                    },
                    *likeDislike,
                ]
            )

            return {"results": cvtJson(comments)}
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def post(self, movieType, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isExistMovies = False

            if movieType == "movie":
                isExistMovies = self.__db["movies"].find_one({"id": str(id)}) != None
            elif movieType == "tv":
                isExistMovies = self.__db["tvs"].find_one({"id": str(id)}) != None
            else:
                raise NotInTypeError("movie", movieType)

            if isExistMovies == True:
                commentForm = request.form

                if len(commentForm.get("content")) == 0:
                    raise DefaultError("Content comment is not allowed empty")

                idComment = str(uuid.uuid4())

                result = None

                if commentForm.get("type") == "children" and "parent_id" in commentForm:
                    comment_document = {
                        "id": idComment,
                        "content": commentForm.get("content"),
                        "user_id": str(jwtUser["id"]),
                        "username": jwtUser["username"],
                        "user_avatar": jwtUser["avatar"],
                        "movie_id": str(id),
                        "movie_type": str(movieType),
                        "parent_id": commentForm.get("parent_id"),
                        "type": "children",
                        # "childrens": 0,
                        # "like": 0,
                        # "dislike": 0,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }

                    if "reply_to" in commentForm:
                        comment_document["reply_to"] = commentForm.get("reply_to")

                    result = self.__db["comments"].insert_one(comment_document)

                    # if resultInsert1.inserted_id != None:
                    #     self.__db["comments"].update_one(
                    #         {
                    #             "id": commentForm.get("parent_id"),
                    #             "movie_id": str(id),
                    #             "movie_type": str(movieType),
                    #             "type": "parent",
                    #         },
                    #         {
                    #             "$inc": {"childrens": 1},
                    #         },
                    #     )

                    if result.inserted_id == None:
                        raise DefaultError("Post comment failed")

                elif commentForm.get("type") == "parent":
                    result = self.__db["comments"].insert_one(
                        {
                            "id": idComment,
                            "content": commentForm.get("content"),
                            "user_id": str(jwtUser["id"]),
                            "username": jwtUser["username"],
                            "user_avatar": jwtUser["avatar"],
                            "movie_id": str(id),
                            "movie_type": str(movieType),
                            "type": "parent",
                            # "parent_id": None,
                            # "childrens": 0,
                            # "like": 0,
                            # "dislike": 0,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now(),
                        }
                    )

                    if result.inserted_id == None:
                        raise DefaultError("Post comment failed")

                if result != None:
                    comment_inserted = self.__db["comments"].find_one({"id": idComment})

                    return {
                        "success": True,
                        "result": {
                            "id": idComment,
                            "content": comment_inserted["content"],
                            "user_id": str(jwtUser["id"]),
                            "username": jwtUser["username"],
                            "user_avatar": jwtUser["avatar"],
                            "movie_id": str(id),
                            "movie_type": str(movieType),
                            "parent_id": comment_inserted.get("parent_id"),
                            "reply_to": comment_inserted.get("reply_to"),
                            "type": comment_inserted.get("type"),
                            "childrens": 0,
                            "like": 0,
                            "dislike": 0,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now(),
                        },
                    }
                else:
                    raise DefaultError("Post comment failed")

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
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except NotInTypeError as e:
            BadRequestMessage(e.message)
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def edit(self, movieType, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isExistMovies = False

            if movieType == "movie":
                isExistMovies = self.__db["movies"].find_one({"id": str(id)}) != None
            elif movieType == "tv":
                isExistMovies = self.__db["tvs"].find_one({"id": str(id)}) != None
            else:
                raise NotInTypeError("movie", movieType)

            if isExistMovies == True:
                commentForm = request.form

                resultUpdate = self.__db["comments"].update_one(
                    {
                        "id": commentForm.get("id"),
                        "user_id": str(jwtUser["id"]),
                        "movie_id": str(id),
                        "movie_type": str(movieType),
                        # "type": commentForm.get("type"),
                    },
                    {
                        "$set": {
                            "content": commentForm.get("content"),
                            "updated": True,
                            "updated_at": datetime.now(),
                        },
                    },
                )

                if resultUpdate.modified_count == 1:
                    return {"success": True, "content": commentForm.get("content")}
                else:
                    raise DefaultError("Update comment failed")
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
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except NotInTypeError as e:
            BadRequestMessage(e.message)
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def delete(self, movieType, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isExistMovies = False

            if movieType == "movie":
                isExistMovies = self.__db["movies"].find_one({"id": str(id)}) != None
            elif movieType == "tv":
                isExistMovies = self.__db["tvs"].find_one({"id": str(id)}) != None
            else:
                raise NotInTypeError("movie", movieType)

            if isExistMovies == True:
                commentForm = request.form

                if commentForm.get("type") == "parent":
                    result1 = self.__db["comments"].delete_one(
                        {
                            "id": commentForm.get("id"),
                            "user_id": str(jwtUser["id"]),
                            "movie_id": str(id),
                            "movie_type": str(movieType),
                            "parent_id": None,
                            "type": "parent",
                        }
                    )

                    childrens = self.__db["comments"].find(
                        {
                            "movie_id": str(id),
                            "movie_type": str(movieType),
                            "parent_id": commentForm.get("id"),
                            "type": "children",
                        }
                    )

                    if len(cvtJson(childrens)) > 0:
                        result2 = self.__db["comments"].delete_many(
                            {
                                "movie_id": str(id),
                                "movie_type": str(movieType),
                                "parent_id": commentForm.get("id"),
                                "type": "children",
                            }
                        )

                        if result1.deleted_count == 1 and result2.deleted_count >= 1:
                            return {
                                "success": True,
                            }
                        else:
                            raise DefaultError("Delete comment failed")
                    elif len(cvtJson(childrens)) == 0:
                        if result1.deleted_count == 1:
                            return {
                                "success": True,
                            }
                        else:
                            raise DefaultError("Delete comment failed")

                elif commentForm.get("type") == "children":
                    resultDel1 = self.__db["comments"].delete_one(
                        {
                            "id": commentForm.get("id"),
                            "user_id": str(jwtUser["id"]),
                            "movie_id": str(id),
                            "movie_type": str(movieType),
                            "parent_id": commentForm.get("parent_id"),
                            "type": commentForm.get("type"),
                        }
                    )

                    # resultUpdate1 = self.__db["comments"].update_one(
                    #     {
                    #         "id": commentForm.get("parent_id"),
                    #         "movie_id": str(id),
                    #         "movie_type": str(movieType),
                    #         "type": "parent",
                    #     },
                    #     {
                    #         "$inc": {"childrens": -1},
                    #     },
                    # )

                    if (
                        resultDel1.deleted_count
                        == 1
                        # and resultUpdate1.modified_count == 1
                    ):
                        return {
                            "success": True,
                        }
                    else:
                        raise DefaultError("Delete comment failed")
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
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except NotInTypeError as e:
            BadRequestMessage(e.message)
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def like(self, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "like",
                }
            )

            isDisLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "dislike",
                }
            )

            if isDisLike != None:
                result = self.__db["commentlikes"].delete_one(
                    {
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "dislike",
                    }
                )

                # result2 = self.__db["comments"].find_one_and_update(
                #     {
                #         "id": id,
                #     },
                #     {
                #         "$inc": {"dislike": -1},
                #     },
                #     return_document=ReturnDocument.AFTER,
                # )

                if result.deleted_count < 1:
                    # or result2 == None:
                    raise DefaultError("Like comment failed")

            if isLike == None:
                result = self.__db["commentlikes"].insert_one(
                    {
                        "id": str(uuid.uuid4()),
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "like",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }
                )

                if result.inserted_id != None:
                    # result2 = self.__db["comments"].find_one_and_update(
                    #     {
                    #         "id": id,
                    #     },
                    #     {
                    #         "$inc": {"like": 1},
                    #     },
                    #     return_document=ReturnDocument.AFTER,
                    # )

                    # if result2 != None:
                    return {
                        "success": True,
                        "action": "like",
                        # "like": result2["like"],
                    }
                    # else:
                    #     raise DefaultError('Like comment failed')

                else:
                    raise DefaultError("Like comment failed")
            else:
                result = self.__db["commentlikes"].delete_one(
                    {
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "like",
                    }
                )

                if result.deleted_count == 1:
                    # result2 = self.__db["comments"].find_one_and_update(
                    #     {
                    #         "id": id,
                    #     },
                    #     {
                    #         "$inc": {"like": -1},
                    #     },
                    #     return_document=ReturnDocument.AFTER,
                    # )

                    # if result2 != None:
                    return {
                        "success": True,
                        "action": "unlike",
                        # "like": result2["like"],
                    }
                    # else:
                    #     raise DefaultError('Unlike comment failed')
                else:
                    raise DefaultError("Unlike comment failed")

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
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def dislike(self, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isDisLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "dislike",
                }
            )

            isLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "like",
                }
            )

            if isLike != None:
                result = self.__db["commentlikes"].delete_one(
                    {
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "like",
                    }
                )

                # result2 = self.__db["comments"].find_one_and_update(
                #     {
                #         "id": id,
                #     },
                #     {
                #         "$inc": {"like": -1},
                #     },
                #     return_document=ReturnDocument.AFTER,
                # )

                if result.deleted_count < 1:
                    # or result2 == None:
                    raise DefaultError("Dislike comment failed")

            if isDisLike == None:
                result = self.__db["commentlikes"].insert_one(
                    {
                        "id": str(uuid.uuid4()),
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "dislike",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }
                )

                if result.inserted_id != None:
                    # result2 = self.__db["comments"].find_one_and_update(
                    #     {
                    #         "id": id,
                    #     },
                    #     {
                    #         "$inc": {"dislike": 1},
                    #     },
                    #     return_document=ReturnDocument.AFTER,
                    # )

                    # if result2 != None:
                    return {
                        "success": True,
                        "action": "dislike",
                        # "dislike": result2["dislike"],
                    }
                    # else:
                    #     raise DefaultError('Dislike comment failed')
                else:
                    raise DefaultError("Dislike comment failed")
            else:
                result = self.__db["commentlikes"].delete_one(
                    {
                        "user_id": jwtUser["id"],
                        "comment_id": id,
                        "type": "dislike",
                    }
                )

                if result.deleted_count == 1:
                    # result2 = self.__db["comments"].find_one_and_update(
                    #     {
                    #         "id": id,
                    #     },
                    #     {
                    #         "$inc": {"dislike": -1},
                    #     },
                    #     return_document=ReturnDocument.AFTER,
                    # )

                    # if result2 != None:
                    return {
                        "success": True,
                        "action": "undislike",
                        # "dislike": result2["dislike"],
                    }
                    # else:
                    # raise DefaultError('Undislike comment failed')
                else:
                    raise DefaultError("Undislike comment failed")

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
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)

    def check_like_dislike(self, id):
        try:
            user_token = request.headers["Authorization"].replace(
                "Bearer ", ""
            ) or request.cookies.get("user_token")

            jwtUser = jwt.decode(
                user_token,
                str(os.getenv("JWT_SIGNATURE_SECRET")),
                algorithms=["HS256"],
            )

            isLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "like",
                }
            )

            if isLike != None:
                return {
                    "success": True,
                    "type": "like",
                }

            isDisLike = self.__db["commentlikes"].find_one(
                {
                    "user_id": jwtUser["id"],
                    "comment_id": id,
                    "type": "dislike",
                }
            )

            if isDisLike != None:
                return {
                    "success": True,
                    "type": "dislike",
                }

            return {
                "success": False,
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
        except DefaultError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)
