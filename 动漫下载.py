import requests
import re
import asyncio
import aiohttp
import aiofiles
import os

def download_mp4(url, filepath):
    response = requests.get(url, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print('视频下载完成')
    
def download_m3u8(url, save_path):
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    with open(save_path, 'wb') as file:
        file.write(response.content)

def read_m3u8_lines(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file.readlines():
            if not line.startswith('#') and line.strip():
                lines.append(line.strip())
    return lines
 
async def download_ts(url, name, session, save_path):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                total_size = int(resp.headers.get('content-length', 0))
                downloaded_size = 0
                print(f"开始下载 {name}，总大小: {total_size} 字节")
                async with aiofiles.open(f"{save_path}/{name}.ts", mode="wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        downloaded_size += len(chunk)
                        await f.write(chunk)
            else:
                print(f"下载 {name} 失败，状态码: {resp.status}")
    except Exception as e:
        print(f"下载 {name} 时发生错误: {e}")


async def aio_download(up_url, m3u8_file, save_path):
    tasks = []
    try:
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(m3u8_file, mode="r", encoding='utf-8') as f:
                number = 1000
                async for line in f:
                    if line.startswith("#"):
                        continue
                    line = line.strip()
                    number += 1
                    ts_url = up_url + line
                    task = asyncio.create_task(download_ts(ts_url, number, session, save_path))
                    tasks.append(task)
            await asyncio.wait(tasks)
    except Exception as e:
        print(f"下载过程中发生错误: {e}")
    finally:
        # 确保资源正确关闭（这里只是示例，实际上 aiohttp.ClientSession 的上下文管理器会自动处理关闭，但为了完整性可以添加类似逻辑）
        await session.close()


#var Vurl = 'https://sf16-sg-default.akamaized.net/obj/tos-alisg-v-0000/oUmeAxfGsZMzLo9Tr2cQfgKATosAyAefsbYEsh';
    
def dmss():
    try:
        print("{0:-^{1}}".format("Pluto伟的动漫搜索器", 50))
        url1 = 'https://www.agedm.org/search?query='
        name = input("请输入番名：")
        print("-"*57)
        html_search1 = requests.get(url1+name)
        search_list = re.findall(r'<h5 class="card-title"><a href=(.*?)</h5>',html_search1.content.decode('utf-8'))
        url2_search = list()
        name_search = list()
        for i,item in enumerate(search_list,1):
            url2_search.append(''.join(re.findall(r'"([^"]+)"',item)))
            name_search.append(''.join(re.findall(r'">(.*?)</a>',item)))
            print(f"{i}、\"{name_search[i-1]}\"")
        choose = int(input("请问你搜索的是哪一个（数字）："))
        url2 = url2_search[choose-1]
        html_search2 = requests.get(url2)
        JiShu = re.findall(r'/1/(\d+)" class="video_detail_spisode_link">',html_search2.content.decode('utf-8'))
        JianJie = ''.join(re.findall(r'<div class="video_detail_desc py-2">(.*?)</div>',html_search2.content.decode('utf-8')))
        find = dict(re.findall(r'<li><span class="detail_imform_tag">(.*?)</span><span class="detail_imform_value">(.*?)</span></li>',html_search2.content.decode('utf-8')))
        dm_id=''.join(re.findall(r'http://www.agedm.org/detail/(\d+)',url2))
        print("{0:-^{1}}".format("查找到以下内容", 50))
        for key, value in find.items():
            print(f"{'':<5}{key}: {value}")
        print("-"*57)
        print("简介：",JianJie)
        print("-"*57)
        print("现有以下集数：")
        print(JiShu)
        print("-"*57)
        play_Ji = input("请问你要播放第几集（数字）：")
        download_url1 = "https://www.agedm.org/play/"+dm_id+"/1/"+play_Ji
        download_resp1 = requests.get(download_url1)
        download_url2 = ''.join(re.findall(r'<iframe id="iframeForVideo" src="([^"]+)" allowfullscreen="allowfullscreen"',download_resp1.content.decode('utf-8')))
        if "vip" in download_url2:
            download_url1 = "https://www.agedm.org/play/"+dm_id+"/2/"+play_Ji
            download_resp1 = requests.get(download_url1)
            download_url2 = ''.join(re.findall(r'<iframe id="iframeForVideo" src="([^"]+)" allowfullscreen="allowfullscreen"',download_resp1.content.decode('utf-8')))
            download_resp2 = requests.get(download_url2)
            m3u8_1_url = ''.join(re.findall(r"var Vurl = '(https://[\w\-\./:]+)';",download_resp2.content.decode('utf-8')))
            #var Vurl = '(https://[\w\-\./:]+)';
            download_m3u8(m3u8_1_url,'./m3u8_1.m3u8')
            url_1 = m3u8_1_url[:m3u8_1_url.rfind("/")]
            m3u8_2_url = url_1 + '/' +''.join(read_m3u8_lines('./m3u8_1.m3u8'))
            url_2 = m3u8_2_url[:m3u8_2_url.rfind("/")] + '/'
            download_m3u8(m3u8_2_url,'./m3u8_2.m3u8')
            print("正在下载中...")
            os.system("mkdir downloads")
            asyncio.run(aio_download(url_2, 'm3u8_2.m3u8', 'downloads'))
            os.system(f"copy /b .\downloads\*.ts {play_Ji}.ts")
            os.system("del .\downloads\*.ts")
            print("下载完成啦！！！")
        else:
            download_resp2 = requests.get(download_url2)
            print(download_resp2.content.decode('utf-8'))
            download_url = ''.join(re.findall(r"var Vurl = '(https://[\w\-\./:]+)'",download_resp2.content.decode('utf-8')))
            print(download_url)
            print("正在下载中...")
            download_mp4(download_url, f'./{str(name_search[choose-1])}-{play_Ji}.mp4')
            print("下载完成啦！！！")
    except (IndexError, KeyError, NameError, TypeError,requests.exceptions.RequestException,ValueError) as e:
        print("\n")
        print("-"*57)
        print("未查找到任何内容")
        print(f"具体错误信息: {e}")
if __name__ == "__main__":
    dmss()
 
