#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《人情世故指南》上游开源仓库同步与自动更新工具
用法：python tools/sync_upstream.py
功能：
1. 检查并拉取原作者 upstream (kkk-bot/HowToGetAlong) 的最新修改
2. 自动合并到本地分支
3. 自动重新编译 Claude 雅致风格的 index.html
4. 提交并推送至 origin (xiaobai5211314/HowToGetAlong)
5. 自动触发 GitHub Actions 部署至生产服务器 (renqing.21212121.xyz)
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, check=True):
    print(f"[*] 执行命令: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"[!] 错误: {res.stderr.strip()}", file=sys.stderr)
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res

def main():
    print("=" * 60)
    print("    《人情世故指南》上游开源仓库同步与自动更新工具")
    print("=" * 60)
    
    # 1. 检查 remote
    remotes = run("git remote -v").stdout
    if "upstream" not in remotes:
        print("[*] 正在添加上游仓库源 upstream: https://github.com/kkk-bot/HowToGetAlong.git")
        run("git remote add upstream https://github.com/kkk-bot/HowToGetAlong.git")

    # 2. 拉取 upstream
    print("[*] 正在从 upstream 获取最新变更...")
    run("git fetch upstream")

    # 3. 检查是否有新提交
    diff = run("git rev-list HEAD..upstream/main --count").stdout.strip()
    if diff == "0":
        print("[✓] 当前仓库已是上游最新版本，无需合并！")
    else:
        print(f"[*] 发现上游存在 {diff} 个新提交，正在合并...")
        run("git merge upstream/main -m 'chore: merge upstream updates'")

    # 4. 重新构建 Claude UI 检索单页
    print("[*] 正在基于最新正文重新编译 Claude UI 检索单页...")
    run(f"{sys.executable} tools/build_claude_ui.py")

    # 5. 检查本地是否有待提交文件
    status = run("git status --porcelain").stdout.strip()
    if status:
        print("[*] 发现变动文件，正在提交至本地 Git...")
        run("git add .")
        run("git commit -m 'feat: sync upstream updates and rebuild Claude UI portal'")
        print("[*] 正在推送至 GitHub 仓库 (origin main)...")
        run("git push origin main")
        print("=" * 60)
        print("🎉 推送成功！GitHub Actions 已自动触发并将最新内容部署至服务器：")
        print("🌐 站点地址: https://renqing.21212121.xyz")
        print("=" * 60)
    else:
        print("[✓] 没有文件需要推送，云端已是最新状态。")

if __name__ == '__main__':
    main()
