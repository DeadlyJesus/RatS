import sys

from RatS.parsers.base_parser import Parser
from RatS.sites.movielens_site import Movielens
from RatS.utils.command_line import print_progress


class MovielensRatingsParser(Parser):
    def __init__(self):
        super(MovielensRatingsParser, self).__init__(Movielens())

    def _parse_ratings(self):
        json_data = self.site.get_json_from_html()
        self.movies_count = json_data['pager']['totalItems']
        pages_count = json_data['pager']['totalPages']
        ratings = json_data['searchResults']

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (self.site.site_name, pages_count, self.movies_count))
        sys.stdout.flush()

        self._parse_ratings_json(ratings)
        for i in range(2, pages_count + 1):
            self.site.browser.get(self._get_ratings_page(i))
            json_data = self.site.get_json_from_html()
            ratings = json_data['searchResults']
            self._parse_ratings_json(ratings)

    def _get_ratings_page(self, i):
        return '%s&page=%i' % (self.site.MY_RATINGS_URL, i)

    def _parse_ratings_json(self, ratings_json):
        for movie_json in ratings_json:
            movie = self._parse_movie_json(movie_json)
            self.movies.append(movie)
            print_progress(len(self.movies), self.movies_count, prefix=self.site.site_name)

    @staticmethod
    def _parse_movie_json(movie_json):
        movie = dict()
        movie['title'] = movie_json['movie']['title']
        movie['year'] = int(movie_json['movie']['releaseYear'])

        movie['movielens'] = dict()
        movie['movielens']['id'] = movie_json['movie']['movieId']
        movie['movielens']['url'] = 'https://movielens.org/movies/%s' % movie['movielens']['id']
        movie['movielens']['my_rating'] = int(movie_json['movieUserData']['rating'] * 2)

        movie['imdb'] = dict()
        movie['imdb']['id'] = movie_json['movie']['imdbMovieId']
        if 'tt' not in movie_json['movie']['imdbMovieId']:
            movie['imdb']['id'] = 'tt%s' % movie['imdb']['id']
        movie['imdb']['url'] = 'http://www.imdb.com/title/%s' % movie['imdb']['id']

        movie['tmdb'] = dict()
        movie['tmdb']['id'] = movie_json['movie']['tmdbMovieId']
        movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/%s' % movie['tmdb']['id']

        return movie