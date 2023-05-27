import pymongo
from pymongo.errors import PyMongoError
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage
from flask import *
from pymongo import ReturnDocument
from configs.database import Database
import os
import jwt


class TV(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def detail_tv(self, id):
        try:
            append_to_response = request.args.get(
                "append_to_response", default="", type=str
            )
            exceptValue = {"images": 0, "credits": 0, "videos": 0}

            if append_to_response != "":
                if "images" in append_to_response.split(","):
                    exceptValue.pop("images")
                if "credits" in append_to_response.split(","):
                    exceptValue.pop("credits")
                if "videos" in append_to_response.split(","):
                    exceptValue.pop("videos")

            tv = self.__db["tvs"].find_one({"id": int(id)}, exceptValue)

            headers = request.headers

            if "Authorization" not in headers:
                if tv != None:
                    return cvtJson(tv)
                else:
                    return {"not_found": True, "result": "Can not find the tv"}
            else:
                user_token = request.headers["Authorization"].replace("Bearer ", "")

                jwtUser = jwt.decode(
                    user_token,
                    str(os.getenv("JWT_TOKEN_SECRET")),
                    algorithms=["HS256"],
                )
                item_lists = self.__db["lists"].find_one(
                    {"id": jwtUser["id"]}, {"items": {"$elemMatch": {"id": int(id)}}}
                )

                if "items" in item_lists:
                    tv = tv | {"in_list": True}
                else:
                    tv = tv | {"in_list": False}

                item_watchlists = self.__db["watchlists"].find_one(
                    {"id": jwtUser["id"]}, {"items": {"$elemMatch": {"id": int(id)}}}
                )

                if "items" in item_watchlists:
                    tv = tv | {
                        "in_history": True,
                        "history_progress": {
                            "duration": item_watchlists["items"][0]["duration"],
                            "percent": item_watchlists["items"][0]["percent"],
                            "seconds": item_watchlists["items"][0]["seconds"],
                        },
                    }
                else:
                    tv = tv | {"in_history": False}

                return cvtJson(tv)

        except jwt.ExpiredSignatureError as e:
            return {"is_token_expired": True, "result": "Token is expired"}
        except jwt.exceptions.DecodeError as e:
            return {"is_invalid_token": True, "result": "Token is invalid"}
        except:
            return {"not_found": True, "result": "Can not find the tv"}

    def add_tv(self):
        try:
            formMovie = request.form
            movie = self.__db["phimles"].find_one({"id": int(formMovie["id"])})
            tv = self.__db["phimbos"].find_one({"id": int(formMovie["id"])})
            if movie == None and tv == None:
                self.__db["phimbos"].insert_one(
                    {
                        "id": int(formMovie["id"]),
                        "name": formMovie["name"],
                        "original_name": formMovie["original_name"],
                        "original_language": formMovie["original_language"],
                        "poster_path": formMovie["poster_path"],
                        "backdrop_path": formMovie["backdrop_path"],
                        "first_air_date": formMovie["first_air_date"],
                        "last_air_date": formMovie["last_air_date"],
                        "genres": json.loads(formMovie["genres"]),
                        "overview": formMovie["overview"],
                        "episode_run_time": int(formMovie["episode_run_time"]),
                        "number_of_episodes": int(formMovie["number_of_episodes"]),
                        "status": formMovie["status"],
                        "views": 0,
                        "media_type": "tv",
                    },
                )
                return {"success": True, "result": "Add tv successfully"}
            else:
                return {
                    "success": False,
                    "already": True,
                    "result": "Tv is already exist",
                }

        except:
            return {"success": False, "result": "Add tv failed"}

    def edit_tv(self, id):
        try:
            formMovie = request.form

            tv = self.__db["hieus"].find_one_and_update(
                {"id": int(id)},
                {
                    "$set": {
                        "name": formMovie["name"],
                        "original_name": formMovie["original_name"],
                        "original_language": formMovie["original_language"],
                        "first_air_date": formMovie["first_air_date"],
                        "last_air_date": formMovie["last_air_date"],
                        "genres": json.loads(formMovie["genres"]),
                        "overview": formMovie["overview"],
                        "episode_run_time": int(formMovie["episode_run_time"]),
                        "number_of_episodes": int(formMovie["number_of_episodes"]),
                        "views": int(formMovie["views"]),
                        "status": formMovie["status"],
                    },
                },
                return_document=ReturnDocument.AFTER,
            )
            return {
                "success": True,
                "result": cvtJson(tv),
                "message": "Edit tv successfully",
            }
        except:
            return {"success": False, "message": "Edit tv failed"}

    def update_view_tv(self, id):
        try:
            tv_dumps = self.__db["tvs"].find_one({"id": int(id)})
            new_views = int(tv_dumps["views"]) + 1

            self.__db["tvs"].update_one(
                {"id": int(id)},
                {
                    "$set": {
                        "views": new_views,
                    },
                },
            )
            return {"success": True, "result": "Update views of tv successfully"}
        except:
            return {"success": False, "result": "Update views of tv failed"}
