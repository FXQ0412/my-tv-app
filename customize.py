#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星河影视 · 一键个性化脚本（在 GitHub Actions 的云端自动运行）
把 box/ 目录里的 TVBox 基础源码改成"你的"APP：应用名、包名、主色、默认设置。

采用"按文件搜索 + 字符串替换"，对基础仓库路径差异有容错——
即使某些项没匹配到，也不会报错，只是跳过该项，不影响最终出包。

想换名字 / 包名 / 颜色，只改下面这段「个性化配置」即可。
"""

import os, re, glob, sys

# ===== 个性化配置（想改就改这里）=====
APP_NAME      = "星河影视"
PACKAGE       = "com.xinghe.starriver"
COLOR_PRIMARY = "#FF4D6D"
COLOR_ACCENT  = "#7C5CFF"
# 基础源码被检出到的目录（和工作流 build.yml 里的 path: box 对应）
SRC           = "box"
# =====================================

def log(msg):
    print("[customize] " + msg)

def find_first(pattern):
    for f in glob.glob(pattern, recursive=True):
        if os.path.isfile(f):
            return f
    return None

def safe_read(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception as e:
        log("读取失败 %s: %s" % (p, e))
        return None

def safe_write(p, t):
    try:
        open(p, "w", encoding="utf-8").write(t)
        return True
    except Exception as e:
        log("写入失败 %s: %s" % (p, e))
        return False

changed = []

# 1) 应用名
sp = find_first(SRC + "/**/res/values/strings.xml")
if sp:
    t = safe_read(sp)
    if t is not None:
        nt = re.sub(r'(<string\s+name="app_name"[^>]*>)[^<]*(</string>)',
                    r'\1' + APP_NAME + r'\2', t)
        if nt != t and safe_write(sp, nt):
            changed.append("app_name -> " + APP_NAME)
        else:
            log("strings.xml 里没找到 app_name，跳过")
    else:
        log("strings.xml 读取异常，跳过应用名")
else:
    log("未找到 strings.xml，跳过应用名")

# 2) 包名（applicationId）—— 只改第一个带 applicationId 的 build.gradle
for bg in glob.glob(SRC + "/**/build.gradle", recursive=True):
    t = safe_read(bg)
    if t is None:
        continue
    if "applicationId" in t:
        nt = re.sub(r'applicationId\s+"[^"]+"',
                    'applicationId "' + PACKAGE + '"', t)
        if nt != t and safe_write(bg, nt):
            changed.append("applicationId -> " + PACKAGE)
        break
else:
    log("未找到含 applicationId 的 build.gradle，跳过包名")

# 3) 主色
cf = find_first(SRC + "/**/res/values/colors.xml")
if cf:
    t = safe_read(cf)
    if t is not None:
        nt = t
        nt = re.sub(r'(<color\s+name="colorPrimary"[^>]*>)[^<]*(</color>)',
                    r'\1' + COLOR_PRIMARY + r'\2', nt)
        nt = re.sub(r'(<color\s+name="colorAccent"[^>]*>)[^<]*(</color>)',
                    r'\1' + COLOR_ACCENT + r'\2', nt)
        if nt != t and safe_write(cf, nt):
            changed.append("主色 -> " + COLOR_PRIMARY + " / " + COLOR_ACCENT)
        else:
            log("colors.xml 里没找到 colorPrimary/colorAccent，跳过主色")
    else:
        log("colors.xml 读取异常，跳过主色")
else:
    log("未找到 colors.xml，跳过主色")

# 4) 默认设置（App.java 的 putDefault，尽力而为）
ap = find_first(SRC + "/**/base/App.java") or find_first(SRC + "/**/App.java")
if ap:
    t = safe_read(ap)
    if t is not None:
        nt = t
        nt = re.sub(r'putDefault\(HawkConfig\.HOME_REC,\s*\d+\)',
                    'putDefault(HawkConfig.HOME_REC, 2)', nt)
        nt = re.sub(r'putDefault\(HawkConfig\.PLAY_TYPE,\s*\d+\)',
                    'putDefault(HawkConfig.PLAY_TYPE, 1)', nt)
        nt = re.sub(r'putDefault\(HawkConfig\.SHOW_PREVIEW,\s*(true|false)\)',
                    'putDefault(HawkConfig.SHOW_PREVIEW, true)', nt)
        if nt != t and safe_write(ap, nt):
            changed.append("默认设置(续播/播放器/预览)")
    else:
        log("App.java 读取异常，跳过默认设置")
else:
    log("未找到 App.java，跳过默认设置（不影响出包）")

if changed:
    log("已自动应用个性化：")
    for c in changed:
        log("  - " + c)
else:
    log("没有改动任何文件（可能与基础仓库结构不符，但编译不受影响）")
