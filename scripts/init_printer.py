#!/usr/bin/env python3
"""
美团热敏打印机 - 引导式配置工具
交互式配置打印机：IP / 端口 / 别名（中文）/ 类型 / 备注
"""

import os
import sys
import json
import socket
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"


# ============== 终端输出美化 ==============
def clear():
    os.system("clear")

def banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║         🖨️  美团热敏打印机 - 引导配置工具               ║
╚══════════════════════════════════════════════════════════╝
""")

def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def tip(text):
    print(f"  💡 {text}")

def ok(text):
    print(f"  ✅ {text}")

def warn(text):
    print(f"  ⚠️  {text}")

def info(text):
    print(f"  ℹ️  {text}")


# ============== 环境检查 ==============
def check_python():
    """检查 Python 版本"""
    try:
        ver = sys.version_info
        ok(f"Python {ver.major}.{ver.minor}.{ver.micro} ✓")
        return True
    except Exception:
        warn("未找到 Python，请先安装 Python 3")
        return False


def check_socket(ip, port):
    """测试打印机是否可达"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, port))
        s.close()
        return True
    except socket.timeout:
        return False
    except ConnectionRefusedError:
        return True  # 连接被拒说明 IP/端口可达
    except Exception:
        return False


# ============== 配置管理 ==============
def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_config(config):
    config["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def new_config():
    return {
        "version": "1.0",
        "printers": [],
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().strftime("%Y-%m-%d")
    }


# ============== 交互式输入 ==============
def ask_yesno(question):
    while True:
        ans = input(f"\n  {question} (y/n): ").strip().lower()
        if ans in ("y", "yes", "是", "１"):
            return True
        if ans in ("n", "no", "否", "２", "q"):
            return False
        print("  请输入 y 或 n")


def ask(question, default=None, required=True):
    while True:
        prompt = f"  {question}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        ans = input(prompt).strip()
        if not ans and default:
            return default
        if not ans and required:
            warn("此项为必填，请输入内容")
            continue
        return ans


def ask_port(default=9100):
    while True:
        ans = input(f"  端口 [默认 {default}]: ").strip()
        if not ans:
            return default
        try:
            port = int(ans)
            if 1 <= port <= 65535:
                return port
            warn("端口号必须在 1-65535 之间")
        except ValueError:
            warn("请输入有效的数字端口号")


def ask_port_with_hint():
    """智能端口询问：先问IP，再判断是否需要询问端口"""
    print()
    # 已知美团热敏打印机默认端口的提示
    print("  💡 提示：美团热敏打印机默认端口为 9100，大多数情况下直接回车即可")
    print()
    while True:
        ans = input("  端口 [直接回车使用默认 9100，或输入自定义端口]: ").strip()
        if not ans:
            print("  ✅ 使用默认端口 9100（美团热敏打印机标准端口）")
            return 9100
        try:
            port = int(ans)
            if 1 <= port <= 65535:
                return port
            warn("端口号必须在 1-65535 之间")
        except ValueError:
            warn("请输入有效的数字端口号")


# ============== 单台打印机配置 ==============
def configure_printer():
    """交互式配置一台打印机"""
    section("📋 配置新打印机")

    # 类型选择
    print("\n  请选择设备类型：")
    types = [
        ("1", "出菜档", "出菜口专用"),
        ("2", "分菜档", "分菜/切配专用"),
        ("3", "前台收银", "前台/收银台"),
        ("4", "后厨主打印", "主厨房打印"),
        ("5", "备菜档", "备菜区"),
        ("6", "小吃档", "小吃/凉菜"),
        ("7", "其他", "自定义用途"),
    ]
    for num, name, desc in types:
        print(f"    {num}. {name} - {desc}")
    print()

    type_choice = input("  请输入编号 [默认 1]: ").strip()
    type_map = dict(types)
    device_type = type_map.get(type_choice, "出菜档")

    # IP 地址
    ip = ask("打印机 IP 地址", required=True)
    if not ip:
        return None

    # 端口智能判断
    port = ask_port_with_hint()
    ip_verified = None

    # IP 有效性验证（可选）
    if ask_yesno("是否验证打印机连通性（推荐）？"):
        print(f"\n  🔍 正在连接 {ip}:{port} ...")
        if check_socket(ip, port):
            ok(f"打印机连接成功！")
        else:
            warn(f"无法连接 {ip}:{port}，请确认 IP/端口是否正确")

    # 别名（中文）
    alias_hint = "后厨" if "后厨" in device_type else ("前台" if "收银" in device_type else "打印机")
    alias = ask(f"设置中文别名（如：{alias_hint}）", required=True)

    # 备注
    remark = ask("备注说明（选填，如：梅林店/南山店）", required=False)

    printer = {
        "alias": alias,
        "ip": ip,
        "port": port,
        "type": device_type,
        "remark": remark
    }

    section("✅ 打印机配置完成")
    print(f"    别名: {alias}")
    print(f"    IP:   {ip}:{port}")
    print(f"    类型: {device_type}")
    if remark:
        print(f"    备注: {remark}")

    return printer


def manage_printers(config):
    """管理已配置的打印机"""
    printers = config.get("printers", [])

    if not printers:
        print("\n  ⚠️  尚未配置任何打印机")
        if ask_yesno("立即添加第一台打印机？"):
            p = configure_printer()
            if p:
                printers.append(p)
                config["printers"] = printers
                save_config(config)
                ok("打印机已保存")
    else:
        while True:
            section("🗂️  当前已配置的打印机")
            for i, p in enumerate(printers, 1):
                print(f"  {i}. {p['alias']}  |  {p['ip']}:{p['port']}  |  {p.get('type','')}")
            print()
            print("  a. 添加新打印机")
            print("  d. 删除打印机")
            print("  q. 返回主菜单")

            choice = input("  请选择: ").strip().lower()

            if choice == "a":
                p = configure_printer()
                if p:
                    # 检查别名是否重复
                    if any(x["alias"] == p["alias"] for x in printers):
                        warn(f"别名 '{p['alias']}' 已存在，将覆盖原配置")
                        printers = [x for x in printers if x["alias"] != p["alias"]]
                    printers.append(p)
                    config["printers"] = printers
                    save_config(config)
                    ok("打印机已保存")
            elif choice == "d":
                if not printers:
                    warn("没有可删除的打印机")
                    continue
                num = input("  输入要删除的编号: ").strip()
                try:
                    idx = int(num) - 1
                    removed = printers.pop(idx)
                    config["printers"] = printers
                    save_config(config)
                    ok(f"已删除: {removed['alias']}")
                except (ValueError, IndexError):
                    warn("无效的编号")
            elif choice == "q":
                break


# ============== 功能引导 ==============
def show_guide():
    banner()
    print("""
  欢迎使用美团热敏打印机技能！

  【技能功能】
    ① 打印任务单  - 向指定打印机发送格式化的任务单/检查单
    ② 定时打印   - 配合定时任务，自动在指定时间触发打印
    ③ 多打印机   - 支持多台打印机，按别名/类型区分

  【快速使用】
    第1步 → 运行 --setup  配置打印机（只需一次）
    第2步 → 使用 --name <别名> 发起打印

  【常用命令】
    --setup    配置/管理打印机
    --list     查看已配置的打印机
    --guide    显示本指南

  【示例】
    打印到后厨:
      python3 print_to_printer.py --name 后厨 --title "早班任务" --content "打卡\\n解冻"

    直接指定IP打印:
      python3 print_to_printer.py --ip 192.168.3.172 --port 9100 --title "测试" --content "内容"

  【打印机类型参考】
    出菜档 / 分菜档 / 前台收银 / 后厨主打印 / 备菜档 / 小吃档
""")
    input("\n  按回车键继续...")


# ============== 主流程 ==============
def main():
    clear()
    banner()

    # 1. 环境检查
    section("🔧 环境检查")
    if not check_python():
        warn("请先安装 Python 3")
        input("\n  按回车键退出...")
        sys.exit(1)
    ok("环境检查通过")

    # 2. 加载或初始化配置
    section("📁 配置文件")
    config = load_config()
    if config:
        count = len(config.get("printers", []))
        ok(f"已加载配置，共 {count} 台打印机")
        tip(f"配置文件: {CONFIG_FILE}")
    else:
        info("未找到配置文件，将创建新配置")
        config = new_config()

    # 3. 主菜单
    while True:
        section("🖨️  配置主菜单")
        print("  1. 配置新打印机（添加/管理）")
        print("  2. 查看当前配置")
        print("  3. 功能使用指南")
        print("  4. 保存并退出")
        print("  5. 放弃更改退出")

        choice = input("\n  请选择 [1-5]: ").strip()

        if choice == "1":
            manage_printers(config)
        elif choice == "2":
            printers = config.get("printers", [])
            if not printers:
                print("\n  ⚠️  暂无配置")
            else:
                section("🖨️  当前打印机配置")
                print(f"  {'别名':<10} {'IP':<16} {'端口':<6} {'类型':<12} {'备注'}")
                print(f"  {'-'*60}")
                for p in printers:
                    print(f"  {p['alias']:<10} {p['ip']:<16} {p['port']:<6} {p.get('type',''):<12} {p.get('remark','')}")
            print()
            input("  按回车键继续...")
        elif choice == "3":
            show_guide()
        elif choice == "4":
            save_config(config)
            clear()
            banner()
            ok(f"配置已保存至: {CONFIG_FILE}")
            print(f"\n  已配置 {len(config.get('printers', []))} 台打印机")
            print("\n  【下一步】")
            print("  发起打印:  python3 print_to_printer.py --name <别名> --title \"标题\" --content \"内容\"")
            print("  查看帮助:  python3 print_to_printer.py --guide")
            print()
            break
        elif choice == "5":
            clear()
            banner()
            print("  已放弃更改，再见！👋\n")
            sys.exit(0)
        else:
            warn("无效选项，请输入 1-5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已中断配置，再见！👋\n")
        sys.exit(0)
