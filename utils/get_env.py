#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/12 17:50
# @Author  : Joker
# @File    : get_env.py
# @Software: PyCharm
import os


def get_env_value(env, default):
    """
    获取环境变量，若有返回值，若无返回默认
    :param env: 环境变量字段
    :param default: 默认
    :return: 获取环境变量，若有返回值，若无返回默认
    """
    str_val = os.environ.get(env)
    return default if str_val is None else str_val


def get_env_bool(env, default):
    """
    获取环境变量 bool 值，若有返回 True / False，若无返回默认
    :param env: 环境变量字段
    :param default: 默认
    :return: 获取环境变量 bool 值，若有返回 True / False，若无返回默认
    """
    str_val = os.environ.get(env)
    return default if str_val is None else str_val == 'True'
