import urllib.request
import json

TOKEN = "f7d387da386580399fb6df96b9097c9f876d3ac5"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"

class BitlyHelper:

    def shorten_url(self,longurl):
        try:
            url = ROOT_URL + SHORTEN.format(TOKEN,longurl)
            response = urllib.request.urlopen(url).read()
            jr = json.loads(response)
            return jr['data']['url']
        except Exception as e:
            print(e)