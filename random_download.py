# -*- coding: utf-8 -*-
"""
new_task: 随机刷下行流量

【脚本功能】
每周在随机选择的几天里，于随机的时间点，执行一次文件下载任务，以产生下行流量。

【V2 版说明】
1.  **随机URL选择**: 每次运行时，会从预设的URL列表中随机挑选一个进行下载。(已实现)
2.  **日志优化**: 下载进度日志调整为每下载 1GB 打印一次，避免日志刷屏。(已实现)
3.  **通知系统更新**: 采用新版青龙推荐的通知方式，脚本会尝试调用集成的 `send` 函数。(已实现)

【使用说明】
1.  将此脚本添加到青龙面板，并设置一个定时任务。推荐设置为每天凌晨不易打扰的时间，例如 `30 3 * * *` (每天凌晨3:30)。
2.  在青龙面板的“依赖管理”中，确保已安装 `requests` 库。
3.  根据需要，修改下方的【可配置参数】。
"""

import requests
import random
import time
import os

# --- 【可配置参数】---

# 每周希望执行下载任务的大约天数 (例如，设置为3就是平均每周跑3天)
DAYS_TO_RUN_PER_WEEK = 4

# 触发后，最长随机延迟多少小时再执行下载 (例如，设置为5，则会在0-5小时内随机选择一个时间点)
MAX_DELAY_HOURS = 3

# 【从此列表中随机选择一个URL进行下载】
# 用于下载测速的大文件URL列表。建议使用稳定、高速的CDN链接。
# 这里默认使用忽悠的文件，可以按需增删。
DOWNLOAD_URLS = [
    "https://autopatchcn.bhsr.com/client/diff/hkrpg_cn/game_3.2.0_3.3.0_hdiff_rfUEDALxLKoRInYi.7z", #9.52 GB
    "https://autopatchcn.juequling.com/package_download/op/client_app/download/20250520103942_LepIQk6e5mKQ7PZ3/VolumeZip/juequling_2.0.0_AS.zip.001", #6.21 GB
    "https://autopatchcn.bh3.com/ptpublic/rel/20250523115648_9RU48di9UxAQIixO/PC/BH3_v8.3.0_f2e1345adb47.7z", #20.95 GB
    # 如果需要更大的文件，可以继续添加链接
    # "https://ash-speed.hetzner.com/10GB.bin",
    # "https://bouygues.testdebit.info/10G.iso",
]

# --- 脚本主逻辑，请勿修改以下内容 ---

def send_notification(title, content):
    """
    【兼容新版青龙通知】
    发送通知。优先尝试使用青龙V2.11+集成的 send 函数，
    如果失败（例如在本地运行），则回退到打印到控制台。
    """
    try:
        from notify import send
        print("检测到青龙内置通知函数，正在调用...")
        send(title, content)
        print("通知已发送。")
    except ImportError:
        print("未找到青龙通知函数，将在控制台打印日志。")
        print("---- 通知开始 ----")
        print(f"标题: {title}")
        print(f"内容:\n{content}")
        print("---- 通知结束 ----")

def format_seconds(seconds):
    """将秒数格式化为易读的时间字符串"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{int(hours)}小时 {int(minutes)}分钟"
    else:
        return f"{int(minutes)}分钟 {int(seconds):.0f}秒"

def download_task(url):
    """执行下载任务，只产生流量，不保存文件"""
    print(f"任务开始：准备从以下随机选择的URL下载文件：\n{url}")
    try:
        start_time = time.time()
        total_downloaded = 0
        
        # 【每下载1GB打印一次日志】
        log_interval_bytes = 1 * 1024 * 1024 * 1024  # 1 GB
        next_log_point = log_interval_bytes

        with requests.get(url, stream=True, timeout=600) as r: # 增加超时以防下载大文件时间过长
            r.raise_for_status()
            chunk_size = 1024 * 1024  # 每次读取1MB
            for chunk in r.iter_content(chunk_size=chunk_size):
                total_downloaded += len(chunk)
                
                # 检查是否达到了下一个日志记录点
                if total_downloaded >= next_log_point:
                    print(f"下载进度: 已完成 {total_downloaded / log_interval_bytes:.0f} GB...")
                    # 更新下一个日志点
                    next_log_point += log_interval_bytes
        
        end_time = time.time()
        duration = end_time - start_time
        # 避免除以零
        if duration == 0: duration = 1 
        speed_mbps = (total_downloaded * 8) / (duration * 1024 * 1024)
        
        summary = (
            f"下载任务成功！\n"
            f"总计下载: {total_downloaded / (1024*1024*1024):.2f} GB\n"
            f"任务耗时: {format_seconds(duration)}\n"
            f"平均速度: {speed_mbps:.2f} Mbps"
        )
        print(summary)
        return True, summary
    except requests.exceptions.RequestException as e:
        error_message = f"下载任务失败！\nURL: {url}\n错误: {e}"
        print(error_message)
        return False, error_message

def main():
    print("="*40)
    print(f"执行【随机刷下行流量】 @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    run_probability = DAYS_TO_RUN_PER_WEEK / 7.0
    
    if random.random() < run_probability:
        print(f"今日命中执行条件 (概率 > {run_probability:.2f})，任务将在随机延迟后启动。")
        
        delay_seconds = random.randint(0, MAX_DELAY_HOURS * 3600)
        print(f"计划延迟: {format_seconds(delay_seconds)}。")
        
        time.sleep(delay_seconds)
        
        print(f"延迟结束，于 {time.strftime('%Y-%m-%d %H:%M:%S')} 正式开始执行下载。")
        # 【随机选择URL】
        target_url = random.choice(DOWNLOAD_URLS)
        success, message = download_task(target_url)
        
        if success:
            send_notification("✅ 随机刷下行流量完成", message)
        else:
            send_notification("❌ 随机刷下行流量失败", message)
            
    else:
        print(f"今日未命中执行条件 (概率 < {run_probability:.2f})，跳过本次任务。")
    
    print("脚本执行完毕。")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()