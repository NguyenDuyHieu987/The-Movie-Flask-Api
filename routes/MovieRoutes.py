from flask import *
from flask_cors import cross_origin
import configs
from controllers.MovieControllers import Movie


def movie_routes(app, cache):
    movie = Movie()
    ## Detail movie

    @app.route("/movie/detail/<id>", methods=["GET"])
    @cross_origin(origins=configs.ALL_ORIGINS_CONFIG)
    # @cache.cached()
    def detail_movie_route(id):
        return movie.detail_movie(id)

    ## Add movie

    @app.route("/movie/add", methods=["POST"])
    @cross_origin(origins=configs.API_ADMIN_ORIGINS_CONFIG)
    def add_movie_route():
        return movie.add_movie()

    ## Edit movie

    @app.route("/movie/edit/<id>", methods=["POST"])
    @cross_origin(origins=configs.API_ADMIN_ORIGINS_CONFIG)
    def edit_movie_route(id):
        return movie.edit_movie(id)

    ## Update view movie

    @app.route("/movie/updateview/<id>", methods=["POST"])
    @cross_origin(origins=configs.ALL_ORIGINS_CONFIG)
    def update_view_movie_route(id):
        return movie.update_view_movie(id)
