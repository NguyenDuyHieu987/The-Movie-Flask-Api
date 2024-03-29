from pymongo.errors import PyMongoError
from utils.JsonResponse import ConvertJsonResponse as cvtJson
from utils.ErrorMessage import BadRequestMessage, InternalServerErrorMessage
from utils.exceptions import NotInTypeError
from flask import *
from configs.database import Database


class Trending(Database):
    def __init__(self):
        self.__db = self.ConnectMongoDB()

    def get_slug(self, type):
        try:
            if type == "all":
                page = request.args.get("page", default=1, type=int) - 1
                limit = request.args.get("limit", default=20, type=int)

                trendings = (
                    self.__db["trendings"].find({}).skip(page * limit).limit(limit)
                )

                return cvtJson(
                    {
                        "page": page + 1,
                        "results": trendings,
                        "total": self.__db["trendings"].count_documents({}),
                        "page_size": limit,
                    }
                )
            else:
                raise NotInTypeError("trending", type)
        except PyMongoError as e:
            InternalServerErrorMessage(e._message)
        except NotInTypeError as e:
            BadRequestMessage(e.message)
        except Exception as e:
            InternalServerErrorMessage(e)
