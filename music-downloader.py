#coding:utf-8
import urllib.request
import urllib.parse
from urllib.parse import urlparse
from mutagen.flac import FLAC
from tqdm import tqdm
from typing import List
import os
import re
import requests
import qq_music

"""
Author: yoke.yue@outlook.com
Version: 1.0.0
"""

# 解锁码，关注微信公众号【黑话君】发送“音乐密码”获取
unlockcode = "7A33"
# 音乐保存目录
music_dir = "W:/music"
# 文件路径
playlist_file = "W:/music/playlist.txt"
# 下载音质，高清：HQ，无损：SQ
quality = "SQ"

def clean_folder_name(album_name):
    # 用正则表达式匹配并替换第一个双引号为全角引号“
    album_name = re.sub(r'"', '“', album_name, count=1)
    
    # 用正则表达式匹配并替换第二个双引号为全角引号”
    album_name = re.sub(r'"', '”', album_name, count=1)
    
    # 替换特定字符为全角
    album_name = album_name.replace('?', '？').replace(':', '：').replace('/', '／')
    
    # 删除其他特殊字符（如< > \ | *）
    album_name = re.sub(r'[<>\\|*]', '', album_name)  # 删除不允许的特殊字符
    
    return album_name

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    # 获取文件总大小
    total_size = int(response.headers.get('content-length', 0))
    # 每次读取 64KB
    block_size = 65536
    # 使用 tqdm 显示进度
    with open(save_path, 'wb') as file, tqdm(
        desc="Downloading", 
        total=total_size, 
        unit='B', 
        unit_scale=True, 
        unit_divisor=1024
    ) as progress_bar:
        for data in response.iter_content(block_size):
            # 写入文件
            file.write(data)
            # 更新进度
            progress_bar.update(len(data))

def match_music_name(name1: str, name2: str) -> bool:
    return (name1 == name2 or name1 in name2 or name2 in name1)

def match_music(music_info: qq_music.MusicSimpleInfo, music_name: str, artist_name: str, quality: str) -> bool:
    if not match_music_name(music_info.songname, music_name):
        return False
    
    if artist_name in music_info.singers:
        if quality == 'SQ' and music_info.hasSQ:
            return True
        elif quality == 'HQ' and music_info.hasHQ:
            return True
    return False

def select_best_match_music(music_list: list[qq_music.MusicInfo],
                            songname: str, albummid: str, artist: str) -> qq_music.MusicInfo:
    # 最优匹配
    for item in music_list:
        if match_music_name(item.songname, songname) and any(singer.name == artist for singer in item.singers) and item.albummid == albummid:
            return item
        
    # 次匹配
    for item in music_list:
        if match_music_name(item.songname, songname) and any(singer.name == artist for singer in item.singers) and not item.albummid:
            return item

    # 最差匹配
    for item in music_list:
        if match_music_name(item.songname, songname) and any(singer.name == artist for singer in item.singers):
            return item
    
    return None


def download_music(music_name: str, artist_name=None, base_url=music_dir, quality=quality):
    
    flacAPI = qq_music.FlacOneAPI(unlockcode)

    qqMusicAPI = qq_music.QQMusicAPI()

    # 搜索音乐信息 flac.one
    search_result = flacAPI.search_music(music_name)
    
    if not search_result:
        raise RuntimeError(f"Not found music(flac.one): {music_name} - {artist_name}")
    
    # 搜索音乐信息 qq.com
    music_list = qqMusicAPI.search_music_list(music_name)

    if not music_list:
        raise RuntimeError(f"Not found music(qq.com): {music_name} - {artist_name}")

    # 如果存在指定歌手
    if artist_name:
        s_music_info = next((item for item in search_result if match_music(item, music_name, artist_name, quality)), None)

    # 默认获取第一首音乐
    if not s_music_info:
        s_music_info = search_result[0]

    # 主唱
    main_artist = s_music_info.singers[0]

    # 查询匹配的音乐
    music_info = select_best_match_music(music_list, s_music_info.songname, s_music_info.albummid, main_artist)
    
    if not music_info:
        raise RuntimeError(f"Not found music(qq.com): {music_name} - {artist_name}")

    # 查询专辑信息
    if music_info.albummid:
        album_info = qqMusicAPI.query_album_info(music_info.albummid)
        # 专辑年份
        album_year = album_info.date.year
        # 专辑名称
        albumname = clean_folder_name(music_info.albumname)
        # 专辑目录名称
        album_dir = f"{albumname} ({album_year})"
    else:
        # 专辑目录名称
        album_dir = f"No Album"

    # 歌曲封面保存路径
    save_cover_path = f"{music_dir}/{main_artist}/{album_dir}/cover.jpg"
    # 如果歌曲封面不存在就下载封面
    if music_info.albummid and not os.path.exists(save_cover_path):

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(save_cover_path), exist_ok=True)

        # 获取歌曲封面下载地址
        music_cover_url = qqMusicAPI.get_music_cover_url(music_info.albummid)

        # 下载歌曲封面并保存的到指定路径
        urllib.request.urlretrieve(music_cover_url, save_cover_path)

    # 艺术家封面保存路径
    sava_artist_cover_path = f"{music_dir}/{main_artist}/artist.jpg"

    # 如果歌曲封面不存在就下载封面
    if not os.path.exists(sava_artist_cover_path):

        singer = next((singer for singer in music_info.singers if singer.name == main_artist), None)

        if singer:
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(sava_artist_cover_path), exist_ok=True)

            # 获取歌曲封面下载地址
            artist_cover_url = qqMusicAPI.get_artist_cover_url(singer.artistid)

            # 下载艺术家封面并保存的到指定路径
            urllib.request.urlretrieve(artist_cover_url, sava_artist_cover_path)
    
    # 获取音乐下载地址
    music_download_url = flacAPI.get_music_download_url(s_music_info.id, quality)

    # 获取音乐文件名
    music_file_name = os.path.basename(urlparse(music_download_url).path)

    # 获取文件名后缀
    music_file_extension = os.path.splitext(music_file_name)[1]

    # 音乐保存路径
    if music_info.cdIdx > 0:
        save_music_file_name = f"{music_info.cdIdx:02} - {music_info.songname}{music_file_extension}"
    else:
        save_music_file_name = f"{music_info.songname}{music_file_extension}"
    save_music_path = f"{base_url}/{main_artist}/{album_dir}/{clean_folder_name(save_music_file_name)}"

    # 如果音乐不存在就下载音乐
    if not os.path.exists(save_music_path):
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(save_music_path), exist_ok=True)
        # 下载音乐
        download_file(music_download_url, save_music_path)

    # 加载 FLAC 文件
    audio = FLAC(save_music_path)

    # 如果歌词不存在
    if not 'lyrics' in audio:
        # 查询歌曲歌词
        music_lyric = qqMusicAPI.query_lyric(music_info.songmid)
            # 如果歌词存在
        if music_lyric:
            # 设置歌词
            audio["lyrics"] = music_lyric

    # 设置歌曲序号
    if hasattr(music_info, "cdIdx") and music_info.cdIdx > 0:
        audio["tracknumber"] = str(music_info.cdIdx)

    # 如果存在发行日期
    if hasattr(music_info, "date"):
        # 设置发行年份
        audio["year"] = str(music_info.date.year)
        # 设置发行日期
        audio["date"] = str(music_info.date.strftime("%Y-%m-%d"))
        
    # 保存修改
    audio.save()


# 读取已下载的文件名
def load_downloaded_files():
    try:
        with open(f"{music_dir}/downloaded_files.txt", "r", encoding="utf-8") as file:
            # 返回已处理行的集合
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        # 如果记录文件不存在，返回空集合
        return set()

# 更新已下载文件记录
def update_downloaded_files(filename):
    with open(f"{music_dir}/downloaded_files.txt", "a", encoding="utf-8") as file:
        # 追加到记录文件
        file.write(f"{filename}\n")

# 更新下载失败文件记录
def update_download_failed_files(filename):
    with open(f"{music_dir}/download_failed_files.txt", "a", encoding="utf-8") as file:
        # 追加到记录文件
        file.write(f"{filename}\n")

# 从播放列表批量下载
def batch_download_music():

    # 加载已下载的文件
    downloaded_files = load_downloaded_files()

    try:

        # 打开文件并逐行读取
        with open(playlist_file, "r", encoding="utf-8") as file:

            # 读取所有行
            lines = file.readlines()

        # 歌单歌曲总数
        total = sum(1 for item in lines if (stripped := item.strip()) and stripped[0] != '#')

        # 当前进度
        index = 0

        for line in lines:

            # 音乐名称，去掉前后空格
            music_name = line.strip()

            # 如果第一个字符是 '#'，则跳过
            if not music_name or music_name[0] == '#':
                artist_name = music_name.split('#', 1)[-1].strip()
                continue
            
            # 如果文件已存在，跳过下载
            filename = f"{artist_name} - {music_name}"

            # 进度+1
            index += 1

            if filename in downloaded_files:
                print(f"[{index}/{total}]已下载：{music_name}")
                continue

            # 输出当前正在下载
            print(f"[{index}/{total}]正在下载：{music_name}")

            try:
                # 下载音乐
                download_music(music_name, artist_name=artist_name)
                # 更新已下载记录
                update_downloaded_files(filename)
            except Exception as e:
                # 如果解锁码错误，则中断
                if isinstance(e, qq_music.APIError) and e.message == "解锁码错误":
                    print(f"当前解锁码已过期：{unlockcode}，请重新设置")
                    return
                print(f"下载文件时发生错误: {e}")
                # 更新下载失败记录
                update_download_failed_files(filename)

    except FileNotFoundError:
        print(f"文件 '{playlist_file}' 未找到！")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")


batch_download_music()

