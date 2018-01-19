import sys
import time

from bs4 import BeautifulSoup

from RatS.base.base_site import Site


class Plex(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='user-account-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Plex, self).__init__(args)

    def _parse_configuration(self):
        self.BASE_URL = self.config[self.site_name]['BASE_URL'] + ":" + self.config[self.site_name]['BASE_PORT']
        self.LOGIN_PAGE = "http://{base_url}/web/index.html#!/login".format(base_url=self.BASE_URL)
        self.MOVIE_SECTION_ID = self._determine_movies_section_id()
        self.SERVER_ID = self._determine_server_id()
        self.MY_RATINGS_URL = 'http://{base_url}/library/sections/{section_id}/all' \
                              '?type=1&sort=rating:desc&X-Plex-Container-Start=0&X-Plex-Container-Size=100'.format(
                                  base_url=self.BASE_URL,
                                  section_id=self.MOVIE_SECTION_ID
                              )

    def _determine_movies_section_id(self):
        sys.stdout.write('\r===== ' + self.site_displayname + ': determine movie section')
        sys.stdout.flush()

        self.browser.get('http://{base_url}/library/sections'.format(base_url=self.BASE_URL))
        time.sleep(1)
        media_sections = BeautifulSoup(self.browser.page_source, 'html.parser')
        time.sleep(1)

        return media_sections.find('directory', attrs={'type': 'movie'})['key']

    def _determine_server_id(self):
        self.browser.get('http://{base_url}/web/index.html#!/settings/server'.format(base_url=self.BASE_URL))
        time.sleep(1)
        return self.browser.current_url.split('/')[-2]
