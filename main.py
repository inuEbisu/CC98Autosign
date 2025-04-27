#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import time
from datetime import datetime
from typing import Optional
from log import logger
from user import User, AuthenticationError, SignInError
import requests


def create_sample_config():
    """创建示例配置文件"""
    sample_config = {
        "users": [
            {"username": "your_username1", "password": "your_password1"},
            {"username": "your_username2", "password": "your_password2"},
        ]
    }
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=4)


def time_format(raw: Optional[str]) -> str:
    if not raw:
        raw = "1970-01-01T08:00:00.0000000"
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

def check_network() -> int:
    """
    浙江大学镜像站提供的检查网络环境的api
    
    Returns:
        0: 非校园网
        1: 校园网 IPv4
        2: 校园网 IPv6
    """
    network_check_api_url = "https://mirrors.zju.edu.cn/api/is_campus_network"
    response = requests.get(network_check_api_url)
    return int(response.text)

def process_user(user_data: dict) -> bool:
    """处理单个用户的签到"""
    user = User()
    try:
        # 登录
        user.login(user_data["username"], user_data["password"])
        logger.success(f"用户 {user_data['username']} 登录成功")

        # 签到
        success = user.sign_in()
        if success:
            logger.success(f"用户 {user_data['username']} 签到成功！")
        else:
            logger.warning(f"用户 {user_data['username']} 今天已经签到过！")
        result = user.get_sign_info()
        if result.get("hasSignedInToday"):
            logger.info(f" · 上次签到时间：{time_format(result.get('lastSignInTime'))}")
            logger.info(f" · 本次获得财富值：{result.get('lastReward')}")
            logger.info(f" · 连续签到天数：{result.get('lastSignInCount')}")

        return True
    except AuthenticationError as e:
        logger.error(f"用户 {user_data['username']} 登录失败：{str(e)}")
        return False
    except SignInError as e:
        logger.error(f"用户 {user_data['username']} 签到失败：{str(e)}")
        return False
    except Exception as e:
        logger.error(f"用户 {user_data['username']} 处理过程中发生错误：{str(e)}")
        return False


def batch():
    if not os.path.exists("config.json"):
        logger.critical("配置文件 config.json 不存在，正在创建示例配置文件...")
        create_sample_config()
        logger.info(
            "已创建示例配置文件 config.json，请修改其中的用户名和密码后重新运行程序"
        )
        raise FileNotFoundError("File does not exist")

    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        if not config.get("users"):
            logger.critical("配置文件中没有找到用户信息！")
            raise ValueError("No user info in config")

        total_users = len(config["users"])
        success_count = 0
        logger.info(f"开始处理 {total_users} 个用户的签到...")
        logger.info("-" * 50)
        for user_data in config["users"]:
            if process_user(user_data):
                success_count += 1
            logger.info("-" * 50)

        logger.info(f"签到完成！成功处理 {success_count}/{total_users} 个用户")
    except json.JSONDecodeError as e:
        logger.critical("配置文件格式错误！请检查 config.json 的格式是否正确")
        raise e
    except Exception as e:
        logger.critical(f"程序运行出错：{str(e)}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CC98自动签到程序")
    parser.add_argument(
        "--loop", action="store_true", help="是否循环执行（默认不循环）"
    )
    args = parser.parse_args()

    while True:
        try:
            batch()
            if not args.loop:
                break
            logger.info("等待 1 小时后再次执行...")
            time.sleep(3600)  # 3600 seconds = 1 hours
        except KeyboardInterrupt:
            logger.warning("程序被用户中断")
            break
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            break
        except Exception as e:
            logger.info("等待 10 秒后重试...")
            time.sleep(10)
            logger.info("重试中...")
