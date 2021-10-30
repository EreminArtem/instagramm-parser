import json
import re

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from instagram_parser.items import InstagramParserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    users = ['iakimchuk24', 'marina_ivanovskay']
    followers = 'https://i.instagram.com/api/v1/friendships/%s/followers/'
    subscribers = 'https://i.instagram.com/api/v1/friendships/%s/following/'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1634577477:AWdQAK0AEOF+wFwWVYjoEuu8uCHn+Pabck9vUxQlFS3/o3VdiZCGuEm4HaF+MLP9EwSytUXe+VNGZWVqv/Pz+z14vr8gT4dClBa6OPYXzPbHCHcU0fUqrO731Bcf4OCxjIcxB4lurkTpWrZPz+Ir'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user})

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        yield response.follow(self.followers % user_id,
                              callback=self.parse_followers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         }
                              )

    def parse_followers(self, response: HtmlResponse, username, user_id):
        loader = ItemLoader(item=InstagramParserItem(), response=response)
        loader.add_value('_id', user_id)
        loader.add_value('name', username)
        loader.add_value('followers', response.json().get('users'))
        yield response.follow(self.subscribers % user_id,
                              callback=self.parse_subscribers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'loader': loader
                                         }
                              )

    def parse_subscribers(self, response: HtmlResponse, username, user_id, loader: ItemLoader):
        loader.add_value('subscribers', response.json().get('users'))
        yield loader.load_item()

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '\"id\":\"\\d+\",\"is_business_account\":\\S{5}', text
        ).group()
        return json.loads('{%s}' % matched).get('id')
