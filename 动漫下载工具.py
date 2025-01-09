import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import messagebox
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
                async with aiofiles.open(f"{save_path}/{name}.ts", mode="wb") as f:
                    async for chunk in resp.content.iter_chunked(1024):
                        downloaded_size += len(chunk)
                        await f.write(chunk)
            else:
                pass
    except Exception as e:
        messagebox.showerror('错误', f'下载第 {name} 个文件时发生错误: {e}')


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
        messagebox.showerror('错误', f'下载文件时发生错误: {e}')
    finally:
        # 确保资源正确关闭（这里只是示例，实际上 aiohttp.ClientSession 的上下文管理器会自动处理关闭，但为了完整性可以添加类似逻辑）
        await session.close()

sign = 0 #用于判断是否点击过搜索按钮

root = tk.Tk()
root.title('动漫下载工具')
root.geometry('395x520')
root.resizable(False, False)
welcome_sign = "请在这里输入动漫名称"

fontStyle = tkFont.Font(family="FangSong", size=20)
entry_text = tk.StringVar()
entry_text.set(welcome_sign)
entry1 = tk.Entry(root,textvariable=entry_text)
entry1['font'] = fontStyle
entry1.place(x=5,y=5,width=330,height=50)
columns = ('0','1')
table = ttk.Treeview(root,columns=columns,show='headings')
table.heading('0', text='ID')
table.column('0', width=77)
table.heading('1', text='动漫标题')
table.column('1', width=308)
table.pack(fill=tk.BOTH, expand=True)
table.place(x=5, y=60, width=385, height=280)
url2_search = list()
name_search = list()
name_text = tk.StringVar()
name_text.set('ID')
name_entry = tk.Entry(root,textvariable=name_text)
name_entry['font'] = fontStyle
name_entry.place(x=5,y=345,width=195,height=50)
download_jishu_entry = tk.StringVar()
download_jishu_entry.set('0')
entry2 = tk.Entry(root,textvariable=download_jishu_entry)
entry2['font'] = fontStyle
entry2.place(x=5,y=455,width=195,height=50)
JiShu = 0
dm_id = ''
choose = 0

def download_ji(dm_id,play_Ji):
    global sign, url2_search, name_search, jishu_entry, JiShu, choose
    download_url1 = "https://www.agedm.org/play/"+dm_id+"/1/"+play_Ji
    download_resp1 = requests.get(download_url1)
    download_url2 = ''.join(re.findall(r'<iframe id="iframeForVideo" src="([^"]+)" allowfullscreen="allowfullscreen"',download_resp1.content.decode('utf-8')))
    try:
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
            os.system("mkdir downloads")
            asyncio.run(aio_download(url_2, 'm3u8_2.m3u8', 'downloads'))
            os.system(f"copy /b .\downloads\*.ts {play_Ji}.ts")
            os.system("del .\downloads\*.ts")
        else:
            download_resp2 = requests.get(download_url2)
            download_url = ''.join(re.findall(r"var Vurl = '(https://[\w\-\./:]+)'",download_resp2.content.decode('utf-8')))
            download_mp4(download_url, f'./{str(name_search[choose-1])}-{play_Ji}.mp4')
    except (IndexError, KeyError, NameError, TypeError,requests.exceptions.RequestException,ValueError) as e:
        messagebox.showerror('错误', f'下载第 {play_Ji} 个文件时发生错误: {e}')

def bottom_search():
    global sign, url2_search, name_search
    if sign == 1:
        messagebox.showwarning('警告','正在忙呢，贝贝！别着急呀！')
    else:
        sign = 1
        table.delete(*table.get_children())
        name = entry1.get()
        url1 = 'https://www.agedm.org/search?query='
        html_search1 = requests.get(url1+name)
        sign = 0
        search_list = re.findall(r'<h5 class="card-title"><a href=(.*?)</h5>',html_search1.content.decode('utf-8'))
        
        for i,item in enumerate(search_list,1):
            url2_search.append(''.join(re.findall(r'"([^"]+)"',item)))
            name_search.append(re.findall(r'">(.*?)</a>',item))
            table.insert('', 'end', values=(i,name_search[i-1],'','',))

def bottom_search_son():
    global sign, url2_search, name_search, jishu_entry, JiShu,dm_id, choose
    if sign == 1:
        messagebox.showwarning('警告','正在忙呢，贝贝！别着急呀！')
    else:
        sign = 1
        choose = int(name_entry.get())
        try:
            url2 = url2_search[choose-1]
            html_search2 = requests.get(url2)
            JiShu_list = re.findall(r'/1/(\d+)" class="video_detail_spisode_link">',html_search2.content.decode('utf-8'))
            dm_id=''.join(re.findall(r'http://www.agedm.org/detail/(\d+)',url2))
            JiShu = len(JiShu_list)
            jishu_entry = tk.StringVar()
            entry = tk.Entry(root, state='disabled', textvariable=jishu_entry)
            jishu_entry.set(f'贝贝，你搜索的动漫目前有{JiShu}集,请问下载哪一集?默认全部下载！')
            entry.place(x=5,y=400,width=385,height=50)
        except (IndexError, KeyError, NameError, TypeError,requests.exceptions.RequestException,ValueError) as e:
            messagebox.showerror('错误', f'搜索第 {choose} 个文件时发生错误: {e}')
        sign = 0
def bottom_download():
    global sign, url2_search, name_search, jishu_entry, JiShu,dm_id
    if sign == 1:
        messagebox.showwarning('警告','正在忙呢，贝贝！别着急呀！')
    else:
        sign = 1
        messagebox.showinfo('提示','开始下载啦！')
        messagebox.showinfo('提示','下载完成后会有提示信息，贝贝耐心等待哦❤')
        if int(download_jishu_entry.get()) == 0:
            for play_Ji in range(1,JiShu):
                download_ji(dm_id,str(play_Ji))
        else:
            play_Ji = int(download_jishu_entry.get())
            download_ji(dm_id,str(play_Ji))
        sign = 0
        messagebox.showinfo('提示','下载完成啦！')

button1 = tk.Button(root,text='搜索',command=bottom_search)
button1.place(x=340,y=5,width=50,height=50)
button2 = tk.Button(root,text='确认',command=bottom_search_son)
button2.place(x=205,y=345,width=185,height=50)
button3 = tk.Button(root,text='开始下载',command=bottom_download)
button3.place(x=205,y=455,width=185,height=50)
root.mainloop()