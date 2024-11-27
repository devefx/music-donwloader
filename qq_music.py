import urllib.request
import urllib.parse
import ssl
import json
import base64
from typing import List
from datetime import datetime

"""
Author: yoke.yue@outlook.com
Version: 1.0.0
"""

# 创建一个 SSL 上下文，忽略证书验证
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class APIError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code
        self.message = message

class Singer():
    def __init__(self, name: str, artistid: str):
        self.name = name
        self.artistid = artistid

class MusicInfo():
    def __init__(self, data: dict):
        # 专辑id
        self.albummid = data.get("albummid")
        # 专辑名
        self.albumname = data.get("albumname")
        # 在专辑中的序号
        self.cdIdx = data.get("cdIdx")
        # 歌曲id
        self.songmid = data.get("songmid")
        # 歌曲名
        self.songname = data.get("songname")
        # 歌手
        self.singers = [Singer(item["name"], item["mid"]) for item in data.get("singer")]
        # 发行日期
        pubtime = data.get("pubtime")
        if pubtime:
            self.date = datetime.fromtimestamp(pubtime)

class AlbumInfo():
    def __init__(self, data: dict):
        # 发行日期
        date_str = data.get("aDate")
        if date_str:
            self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        # 发行公司
        self.company = data.get("company")
        # 描述
        self.desc = data.get("desc")
        # 类型
        self.genre = data.get("genre")
        # 专辑名称
        self.name = data.get("name")
        # 专辑歌曲数
        self.total = data.get("total")

class MusicSimpleInfo():
    def __init__(self, data: dict):
        # 音乐id
        self.id = data.get("id")
        # 专辑id
        self.albummid = data.get("albumId")
        # 专辑名
        self.albumname = data.get("albumName")
        # 歌曲名
        self.songname = data.get("name")
        # 平台
        self.platform = data.get("platform")
        # 歌手
        self.singers = data.get("singers")
        # 是否有无损音质
        self.hasSQ = data.get("hasSQ")
        # 是否有高清音质
        self.hasHQ = data.get("hasHQ")


class QQMusicAPI:

    def search_music_list(self, music_name: str) -> list[MusicInfo]:
        # 目标 URL
        url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&n=20&w={music_name}&format=json"

        encoded_url = urllib.parse.quote(url, safe=":/?=&")

        # 自定义请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
        }

        # 对 URL 进行编码
        request = urllib.request.Request(encoded_url, headers=headers)

        # 发起 HTTPS 请求
        with urllib.request.urlopen(request, context=ssl_context) as response:
            # 获取响应内容
            content = response.read().decode("utf-8")
            # 将 JSON 字符串解析为 Python 对象
            data = json.loads(content)
            # 获取响应状态码
            code = data["code"]
            # 如果正常返回搜索结果
            if code == 0:
                return [MusicInfo(item) for item in data["data"]["song"]["list"]]
            else:
                raise APIError(data["message"], code)
    
    def query_lyric(self, songmid: str) -> str:
        # 目标 URL
        url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?format=json&songmid={songmid}&loginUin=0&hostUin=0&inCharset=utf8&notice=0&platform=yqq.json&needNewCode=0"

        encoded_url = urllib.parse.quote(url, safe=":/?=&")

        # 自定义请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
        }

        # 对 URL 进行编码
        request = urllib.request.Request(encoded_url, headers=headers)

        # 发起 HTTPS 请求
        with urllib.request.urlopen(request, context=ssl_context) as response:
            # 获取响应内容
            content = response.read().decode("utf-8")
            # 将 JSON 字符串解析为 Python 对象
            data = json.loads(content)
            # 获取响应状态码
            code = data["code"]
            # 如果正常返回歌词
            if code == 0:
                # 获取歌词
                return base64.b64decode(data["lyric"]).decode('utf-8')
            else:
                raise APIError(data["message"], code)
    
    def query_album_info(self, albummid: str) -> AlbumInfo:
        # 目标 URL
        url = f"https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={albummid}&g_tk=1278911659&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0"

        encoded_url = urllib.parse.quote(url, safe=":/?=&")

        # 自定义请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
        }

        # 对 URL 进行编码
        request = urllib.request.Request(encoded_url, headers=headers)

        # 发起 HTTPS 请求
        with urllib.request.urlopen(request, context=ssl_context) as response:
            # 获取响应内容
            content = response.read().decode("utf-8")
            # 将 JSON 字符串解析为 Python 对象
            data = json.loads(content)
            # API响应状态码
            code = data["code"]
            # 如果正常返回专辑信息
            if code == 0:
                return AlbumInfo(data["data"])
            else:
                raise APIError(data["message"], code)
            
    def get_music_cover_url(self, albumid: str, quality = "800x800") -> str:
        return f"https://y.qq.com/music/photo_new/T002R{quality}M000{albumid}.jpg?max_age=2592000"

    def get_artist_cover_url(self, artistid: str, quality = "800x800") -> str:
        return f"https://y.qq.com/music/photo_new/T001R800x800M000{artistid}.jpg?max_age=2592000"

class FlacOneAPI:
    def __init__(self, unlockcode):
        self.unlockcode = unlockcode

    def search_music(self, music_name: str) -> list[MusicSimpleInfo]:
        # 目标 URL
        url = f'https://api.flac.life/search/qq?keyword={music_name}&page=1&size=30'

        encoded_url = urllib.parse.quote(url, safe=":/?=&")

        # 自定义请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://flac.one/'
        }

        # 对 URL 进行编码
        request = urllib.request.Request(encoded_url, headers=headers)

        # 发起 HTTPS 请求
        with urllib.request.urlopen(request, context=ssl_context) as response:
            # 获取响应内容
            content = response.read().decode("utf-8")
            # 将 JSON 字符串解析为 Python 对象
            data = json.loads(content)
            # 获取响应状态码
            code = data["code"]
            # 如果正常返回搜索结果
            if code == 200:
                return [MusicSimpleInfo(item) for item in data["result"]["list"]]
            else:
                raise APIError(data["message"], code)

    def get_music_download_url(self, music_id: str, quality: str) -> str:
        # 下载音质
        if quality == "SQ":
            br = "flac"
        elif quality == "HQ":
            br = "320"

        # 目标 URL
        url = f"https://api.flac.life/url/qq/{music_id}/{br}"

        # 自定义请求头
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://flac.one/',
            'Unlockcode': self.unlockcode
        }

        # 对 URL 进行编码
        request = urllib.request.Request(url, headers=headers)

        # 发起 HTTPS 请求
        with urllib.request.urlopen(request, context=ssl_context) as response:
            # 获取响应状态码
            status_code = response.getcode()
            # 获取响应内容
            content = response.read().decode("utf-8")
            # 将 JSON 字符串解析为 Python 对象
            data = json.loads(content)
            # 获取响应状态码
            code = data["code"]
            # 如果正常返回搜索结果
            if code == 200:
                return data["result"]
            else:
                raise APIError(data["message"], code)
