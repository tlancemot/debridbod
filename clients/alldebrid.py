import httpx
from dotenv import load_dotenv
import os

load_dotenv()
APP_NAME = os.getenv('APP_NAME')
ALLDEBRID_TOKEN = os.getenv('ALLDEBRID_TOKEN')

class AllDebrid():

    base_url = "https://api.alldebrid.com/v4/"

    def unlockLink(self, link):
        api_url = f"{self.base_url}link/unlock?agent={APP_NAME}&apikey={ALLDEBRID_TOKEN}&link={link}"
        r = httpx.get(api_url)
        content = r.json()
        if content['status'] == "success":
            if "infos" in content['data']  and "error" in content['data']['infos'][0]:
                return {"status": "error", "message": "{}:{}".format(content['data']['infos'][0]['error']['code'], content['data']['infos'][0]['error']['message'])}
            else:
                return {"status": "success", "message": content['data']['link']}
        else :
            return {"status": "error", "message": content['error']['message']}
    

    def upload_torrent(self, torrent_file):
        api_url = f"{self.base_url}magnet/upload/file?agent={APP_NAME}&apikey={ALLDEBRID_TOKEN}"
        files = {'files[]': (torrent_file, open(torrent_file, 'rb'), 'multipart/form-data')}
        r = httpx.post(api_url, files=files)
        return r.json()
    
    def magnet_info(self, magnet_id: int):
        api_url = f"{self.base_url}magnet/status?agent={APP_NAME}&apikey={ALLDEBRID_TOKEN}&id={magnet_id}"
        r = httpx.get(api_url)
        return r.json()
