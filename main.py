#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests
import ZJUWebVPN

from log import logger
from user import AuthenticationError, SignInError, User


def create_sample_config() -> None:
    """创建示例配置文件"""
    sample_config = {
        "webvpn": {
            "username": "your_webvpn_username",
            "password": "your_webvpn_password",
        },
        "users": [
            {"username": "your_username1", "password": "your_password1"},
            {"username": "your_username2", "password": "your_password2"},
        ],
    }
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=4)


def time_format(raw: Optional[str]) -> str:
    if not raw:
        return "1970-01-01 08:00:00"

    # 处理包含时区信息的格式
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    # 标准化微秒部分为6位
    if "." in raw:
        date_part, time_part = raw.split(".")
        time_part = time_part.split("+")[0].split("-")[0]  # 提取微秒部分
        if len(time_part) > 6:
            time_part = time_part[:6]  # 截断超过6位的微秒
        elif len(time_part) < 6:
            time_part = time_part.ljust(6, "0")  # 补全不足6位的微秒
        normalized = f"{date_part}.{time_part}"
    else:
        normalized = raw

    # 解析时间
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as e:
        logger.error(f"时间解析失败: {normalized}, 错误: {str(e)}")
        return "Invalid time format"

    # 转换到北京时间 (UTC+8)
    dt = dt.astimezone(timezone(timedelta(hours=8)))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def process_user(
    user_data: Dict[str, str], session: requests.Session = requests.Session()
) -> bool:
    """处理单个用户的签到"""
    user = User(session)
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


def batch(config: Dict[str, Any], session: requests.Session) -> None:
    """批量处理用户签到

    Args:
        config: 配置信息字典
        session: 已初始化的会话对象
    """
    if not config.get("users"):
        logger.critical("配置文件中没有找到用户信息！")
        raise ValueError("No user info in config")

    total_users = len(config["users"])
    success_count = 0
    logger.info(f"开始处理 {total_users} 个用户的签到...")
    logger.info("-" * 50)
    for user_data in config["users"]:
        if process_user(user_data, session):
            success_count += 1
        logger.info("-" * 50)

    logger.info(f"签到完成！成功处理 {success_count}/{total_users} 个用户")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CC98自动签到程序")
    parser.add_argument(
        "--loop", action="store_true", help="是否循环执行（默认不循环）"
    )
    args = parser.parse_args()

    while True:
        try:
            # 检查配置文件
            if not os.path.exists("config.json"):
                logger.critical("配置文件 config.json 不存在，正在创建示例配置文件...")
                create_sample_config()
                logger.info(
                    "已创建示例配置文件 config.json，请修改其中的用户名和密码后重新运行程序"
                )
                raise FileNotFoundError("File does not exist")

            # 读取配置文件
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)

            # 检查网络环境
            network_type = ZJUWebVPN.check_network()
            network_types = ["非校园网", "校园网 IPv4", "校园网 IPv6"]
            logger.info(f"当前网络环境：{network_types[network_type]}")

            # 初始化会话
            if not network_type:
                if not config.get("webvpn"):
                    logger.critical(
                        "当前网络环境非校园网，请在 config.json 中配置 WebVPN 用户名和密码"
                    )
                    raise ValueError("No webvpn info in config")
                else:
                    try:
                        session = ZJUWebVPN.ZJUWebVPNSession(
                            config["webvpn"]["username"], config["webvpn"]["password"]
                        )
                        logger.success("WebVPN 登录成功")
                    except Exception as e:
                        logger.error(f"WebVPN 登录失败：{str(e)}")
                        raise e
            else:
                session = requests.Session()

            # 执行批量签到
            batch(config, session)

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
            logger.critical(f"发生错误：{str(e)}")
            logger.info("等待 10 秒后重试...")
            time.sleep(10)
            logger.info("重试中...")
