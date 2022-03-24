import configparser
import logging
import webbrowser

import requests
from ratelimit import limits, sleep_and_retry
from requests_oauthlib import OAuth2Session

from .teamleaderObjects import *

REDIRECT_URI = "https://localhost:3000/oauth.php"
TOKEN_SITE = "https://app.teamleader.eu/oauth2/access_token"
AUTHORIZE_URI = "https://app.teamleader.eu/oauth2/authorize"
REFRESH_URL = "https://app.teamleader.eu/oauth2/access_token"


class Client:
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        teamleader_token_file_name=None,
        config_file_path=None,
        client: OAuth2Session = None,
    ):
        if client:
            self.client = client
        else:
            if config_file_path:
                config = configparser.ConfigParser()
                config_file_path = os.path.abspath(config_file_path)
                if not os.path.isfile(config_file_path):
                    raise FileNotFoundError("Config file not found")
                config.read(config_file_path)
                client_id = config["teamleader"]["CLIENT_ID"]
                client_secret = config["teamleader"]["CLIENT_SECRET"]
                teamleader_token_file_name = config["teamleader"]["TOKEN_FILE_PATH"]

            if not (client_id and client_secret and teamleader_token_file_name):
                raise ValueError("All parameters should be filled")

            self.teamleader_token_file_name = teamleader_token_file_name
            self.client = OAuth2Session(
                client_id,
                token=self._get_token(client_id=client_id, client_secret=client_secret),
                auto_refresh_url=REFRESH_URL,
                auto_refresh_kwargs={
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                token_updater=self._token_saver,
            )
        self.departments = Departments(self.get_teamleader, self.post_teamleader)
        self.users = Users(self.get_teamleader, self.post_teamleader)
        self.projects = Projects(self.get_teamleader, self.post_teamleader)
        self.custom_fields = CustomFields(self.get_teamleader, self.post_teamleader)
        self.worktypes = WorkTypes(self.get_teamleader, self.post_teamleader)
        self.contacts = Contacts(self.get_teamleader, self.post_teamleader)
        self.companies = Companies(self.get_teamleader, self.post_teamleader)
        self.businesstypes = BusinessTypes(self.get_teamleader, self.post_teamleader)
        self.tags = Tags(self.get_teamleader, self.post_teamleader)
        self.dealphases = DealPhases(self.get_teamleader, self.post_teamleader)
        self.dealsources = DealSources(self.get_teamleader, self.post_teamleader)
        self.tasks = Tasks(self.get_teamleader, self.post_teamleader)
        self.invoices = Invoices(self.get_teamleader, self.post_teamleader)
        self.events = Events(self.get_teamleader, self.post_teamleader)
        self.webhooks = Webhooks(self.get_teamleader, self.post_teamleader)
        self.timetracking = TimeTracking(self.get_teamleader, self.post_teamleader)
        self.migrate = Migrate(self.get_teamleader, self.post_teamleader)
        self.deals = Deals(self.get_teamleader, self.post_teamleader)
        self.lostreasons = LostReasons(self.get_teamleader, self.post_teamleader)
        self.teams = Teams(self.get_teamleader, self.post_teamleader)

    def _get_token(self, client_id, client_secret):
        try:
            return self._token_open()
        except FileNotFoundError:
            return self._request_new_token(client_id, client_secret)

    def _token_saver(self, local_token):
        with open(self.teamleader_token_file_name, "wb") as output:
            pickle.dump(local_token, output, protocol=5)
        print("token saved")

    def _token_open(self):
        with open(self.teamleader_token_file_name, "rb") as input:
            return pickle.load(input)

    def _request_new_token(self, client_id, client_secret):
        oauth = OAuth2Session(client_id, redirect_uri=REDIRECT_URI)
        authorization_url, _ = oauth.authorization_url(
            AUTHORIZE_URI,
        )
        webbrowser.open_new(authorization_url)
        authorization_response = input("Enter the full callback URL")
        return oauth.fetch_token(
            TOKEN_SITE,
            authorization_response=authorization_response,
            client_id=client_id,
            client_secret=client_secret,
        )

    @sleep_and_retry
    @limits(calls=100, period=60)
    def _request_method(self, method, url_addition, *args, **kwargs):
        response = method("https://api.teamleader.eu/" + url_addition, *args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logging.info(response.json())
            raise e
        finally:
            return response

    def get_teamleader(self, url_addition, *args, **kwargs):
        return self._request_method(self.client.get, url_addition, *args, **kwargs)

    def post_teamleader(self, url_addition, *args, **kwargs):
        return self._request_method(self.client.post, url_addition, *args, **kwargs)
