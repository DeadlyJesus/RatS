from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.tmdb.tmdb_site import TMDB


class TMDBRatingsParser(RatingsParser):
    def __init__(self, args):
        super(TMDBRatingsParser, self).__init__(TMDB(args), args)

    def _get_ratings_page(self, i):
        return '{url}?page={page_number}'.format(url=self.site.MY_RATINGS_URL, page_number=i)

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find(class_='results').find(class_='pagination').find('span').
                   get_text().split(' ')[0].replace('(', ''))

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        return int(movie_ratings_page.find(class_='results').find(class_='pagination').
                   get_text().split(' ')[-3])

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find(class_='results').find_all('div', class_='item')

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find('p').find('a').get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile.find('p').find('a')['href'].split('/')[-1]

    @staticmethod
    def _get_movie_url(movie_tile):
        return 'https://www.themoviedb.org' + movie_tile.find('p').find('a')['href']

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = int(movie_details_page.find(class_='release_date').get_text().replace('(', '').replace(')', ''))
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = self._get_movie_my_rating(movie_details_page)

    @staticmethod
    def _get_movie_my_rating(movie_details_page):
        return int(float(movie_details_page.find(id='rating_input')['value']) * 2)
