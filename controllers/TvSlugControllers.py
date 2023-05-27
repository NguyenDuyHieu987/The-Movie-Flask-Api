import pymongo
from pymongo.errors import PyMongoError
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage, InternalServerErrorMessage
from utils.exceptions import NotInTypeError
from flask import *
from configs.database import Database


class TVSlug(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def tv_slug(self, slug):
        try:
            if slug == "phimbo":
                page = (request.args.get("page", default=1, type=int)) - 1
                phimbo = cvtJson(
                    self.__db["tvs"]
                    .find(
                        {},
                        {
                            "images": 0,
                            "credits": 0,
                            "videos": 0,
                            "production_companies": 0,
                            "seasons": 0,
                        },
                    )
                    .skip(page * 20)
                    .limit(20)
                )

                return {
                    "page": page + 1,
                    "results": phimbo,
                    "total": self.__db["tvs"].count_documents({}),
                    "page_size": 20,
                }
            elif slug == "airingtoday":
                page = request.args.get("page", default=1, type=int) - 1
                nowplaying = cvtJson(
                    self.__db["tvairingtodays"].find({}).skip(page * 20).limit(20)
                )
                return {
                    "page": page + 1,
                    "results": nowplaying,
                    "total": self.__db["tvairingtodays"].count_documents({}),
                    "page_size": 20,
                }
            elif slug == "ontheair":
                page = request.args.get("page", default=1, type=int) - 1
                upcoming = cvtJson(
                    self.__db["tvontheairs"].find({}).skip(page * 20).limit(20)
                )

                return {
                    "page": page + 1,
                    "results": upcoming,
                    "total": self.__db["tvontheairs"].count_documents({}),
                    "page_size": 20,
                }
            elif slug == "popular":
                page = request.args.get("page", default=1, type=int) - 1
                popular = cvtJson(
                    self.__db["tvpopulars"].find({}).skip(page * 20).limit(20)
                )

                return {
                    "page": page + 1,
                    "results": popular,
                    "total": self.__db["tvpopulars"].count_documents({}),
                    "page_size": 20,
                }
            elif slug == "toprated":
                page = request.args.get("page", default=1, type=int) - 1
                toprated = cvtJson(
                    self.__db["tvtoprateds"].find({}).skip(page * 20).limit(20)
                )
                return {
                    "page": page + 1,
                    "results": toprated,
                    "total": self.__db["tvtoprateds"].count_documents({}),
                    "page_size": 20,
                }
            else:
                raise NotInTypeError("movie slug", slug)
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except NotInTypeError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)
