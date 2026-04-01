import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "llm_api_configs.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"providers": []}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"已保存到 {CONFIG_FILE}")


def find_provider(config, name):
    return next((p for p in config["providers"] if p["name"] == name), None)


def show_providers(config, header=None):
    if header:
        print(f"\n{header}")
    if not config["providers"]:
        print("  （暂无任何厂商）")
        return []
    for i, p in enumerate(config["providers"], 1):
        key_count = len(p["keys"])
        model_count = len(p["models"])
        print(f"  {i}. {p['name']}  |  keys={key_count}  models={model_count}")
    return config["providers"]


# ---------- 增 ----------

def add_provider(config, name, api_url):
    if find_provider(config, name):
        print(f"  提供商 '{name}' 已存在，跳过。")
        return config, False
    config["providers"].append({
        "name": name,
        "api_url": api_url,
        "keys": [],
        "models": []
    })
    print(f"  已添加: {name}")
    return config, True


def add_key(config, provider_name, key, expires=None):
    p = find_provider(config, provider_name)
    if not p:
        print(f"  提供商 '{provider_name}' 不存在。")
        return config, False
    p["keys"].append({"key": key, "expires": expires})
    print(f"  已为 {provider_name} 添加 key (过期: {expires})")
    return config, True


def add_models(config, provider_name, models):
    p = find_provider(config, provider_name)
    if not p:
        print(f"  提供商 '{provider_name}' 不存在。")
        return config, False
    added = 0
    for m in models:
        if m not in p["models"]:
            p["models"].append(m)
            added += 1
    print(f"  新增 {added} 个模型（共 {len(p['models'])} 个）")
    return config, True


# ---------- 删 ----------

def remove_provider(config, name):
    before = len(config["providers"])
    config["providers"] = [p for p in config["providers"] if p["name"] != name]
    return config, len(config["providers"]) < before


def remove_key(config, provider_name, key):
    p = find_provider(config, provider_name)
    if not p:
        return config, False
    before = len(p["keys"])
    p["keys"] = [k for k in p["keys"] if k["key"] != key]
    return config, len(p["keys"]) < before


def remove_model(config, provider_name, model):
    p = find_provider(config, provider_name)
    if not p:
        return config, False
    if model in p["models"]:
        p["models"].remove(model)
        return config, True
    return config, False


# ---------- 查 ----------

def list_all(config):
    if not config["providers"]:
        print("暂无任何提供商配置。")
        return
    for p in config["providers"]:
        print(f"\n{'='*50}")
        print(f"  提供商: {p['name']}")
        print(f"  API URL: {p['api_url']}")
        print(f"  Keys ({len(p['keys'])}):")
        if p["keys"]:
            for k in p["keys"]:
                print(f"    - {k['key'][:15]}...  过期: {k['expires']}")
        else:
            print(f"    （无）")
        print(f"  Models ({len(p['models'])}):")
        if p["models"]:
            for m in p["models"]:
                print(f"    - {m}")
        else:
            print(f"    （无）")


def query(config, provider_name=None, model=None):
    providers = config["providers"]
    if provider_name:
        providers = [p for p in providers if provider_name.lower() in p["name"].lower()]
    if model:
        providers = [p for p in providers if model in p["models"]]
    if not providers:
        print("未找到匹配的提供商。")
        return
    for p in providers:
        print(f"\n{p['name']} | {p['api_url']}")
        print(f"  Keys: {[k['key'] for k in p['keys']]}")
        print(f"  Models: {p['models']}")


# ---------- 交互式菜单 ----------

def choose_provider(config, prompt="请选择厂商"):
    print(f"\n--- 选择厂商 ---")
    providers = show_providers(config)
    if not providers:
        print("  （无厂商，请先到主菜单 2 添加）")
        return None
    while True:
        s = input(f"{prompt}（1-{len(providers)}，0取消）: ").strip()
        if s == "0":
            return None
        try:
            idx = int(s) - 1
            if 0 <= idx < len(providers):
                return providers[idx]["name"]
            print(f"  范围超出，请输入 1-{len(providers)}")
        except ValueError:
            print("  请输入数字")


def main():
    print("=== LLM API 配置管理 ===\n")
    config = load_config()

    while True:
        print("\n--- 主菜单 ---")
        print("  1. 查看所有配置")
        print("  2. 添加提供商")
        print("  3. 为提供商添加 key")
        print("  4. 为提供商添加模型")
        print("  5. 删除提供商")
        print("  6. 删除 key")
        print("  7. 删除模型")
        print("  8. 查询（按厂商名或模型名过滤）")
        print("  0. 保存并退出")
        print("  q. 不保存直接退出")
        choice = input("\n请选择: ").strip()

        if choice in ("q", "Q"):
            print("已退出，未保存。")
            break

        elif choice == "0":
            save_config(config)
            break

        # ---- 查看 ----
        elif choice == "1":
            list_all(config)

        # ---- 添加提供商 ----
        elif choice == "2":
            while True:
                print("\n--- 添加提供商 ---")
                name = input("  名称 (如 Anthropic，b返回上级): ").strip()
                if name.lower() == "b":
                    break
                if not name:
                    print("  名称不能为空")
                    continue
                url = input("  API URL: ").strip()
                config, ok = add_provider(config, name, url)
                if ok:
                    while True:
                        print(f"\n  继续为 '{name}' 添加内容？")
                        print("    k. 添加 key")
                        print("    m. 添加模型")
                        print("    b. 返回上级")
                        n = input("  选择: ").strip().lower()
                        if n == "b":
                            break
                        elif n == "k":
                            key = input("    API Key: ").strip()
                            expires = input("    过期时间 (可回车留空): ").strip() or None
                            config, _ = add_key(config, name, key, expires)
                        elif n == "m":
                            models_str = input("    模型列表 (逗号分隔): ").strip()
                            models = [m.strip() for m in models_str.split(",") if m.strip()]
                            if models:
                                config, _ = add_models(config, name, models)
                        else:
                            print("    无效选项")
                break

        # ---- 添加 key ----
        elif choice == "3":
            provider_name = choose_provider(config, "选择要添加 key 的厂商")
            if provider_name is None:
                continue
            key = input("  API Key: ").strip()
            if not key:
                print("  key 不能为空，跳过。")
                continue
            expires = input("  过期时间 (可回车留空): ").strip() or None
            config, _ = add_key(config, provider_name, key, expires)

        # ---- 添加模型 ----
        elif choice == "4":
            provider_name = choose_provider(config, "选择要添加模型的厂商")
            if provider_name is None:
                continue
            models_str = input("  模型列表 (逗号分隔): ").strip()
            if not models_str:
                print("  模型不能为空，跳过。")
                continue
            models = [m.strip() for m in models_str.split(",") if m.strip()]
            if models:
                config, _ = add_models(config, provider_name, models)

        # ---- 删除提供商 ----
        elif choice == "5":
            provider_name = choose_provider(config, "选择要删除的厂商")
            if provider_name is None:
                continue
            confirm = input(f"  确认删除 '{provider_name}' 吗？(y/n): ").strip().lower()
            if confirm == "y":
                config, deleted = remove_provider(config, provider_name)
                if deleted:
                    print(f"  已删除: {provider_name}")

        # ---- 删除 key ----
        elif choice == "6":
            provider_name = choose_provider(config, "选择厂商")
            if provider_name is None:
                continue
            p = find_provider(config, provider_name)
            if not p["keys"]:
                print("  该厂商暂无 key。")
                continue
            print(f"  Keys:")
            for i, k in enumerate(p["keys"], 1):
                print(f"    {i}. {k['key'][:15]}...  过期: {k['expires']}")
            s = input(f"  输入编号删除（1-{len(p['keys'])}，0取消）: ").strip()
            if s == "0":
                continue
            try:
                idx = int(s) - 1
                if 0 <= idx < len(p["keys"]):
                    removed_key = p["keys"].pop(idx)["key"]
                    print(f"  已删除 key: {removed_key[:15]}...")
            except ValueError:
                print("  无效输入。")

        # ---- 删除模型 ----
        elif choice == "7":
            provider_name = choose_provider(config, "选择厂商")
            if provider_name is None:
                continue
            p = find_provider(config, provider_name)
            if not p["models"]:
                print("  该厂商暂无模型。")
                continue
            print(f"  Models:")
            for i, m in enumerate(p["models"], 1):
                print(f"    {i}. {m}")
            s = input(f"  输入编号删除（1-{len(p['models'])}，0取消）: ").strip()
            if s == "0":
                continue
            try:
                idx = int(s) - 1
                if 0 <= idx < len(p["models"]):
                    removed = p["models"].pop(idx)
                    print(f"  已删除模型: {removed}")
            except ValueError:
                print("  无效输入。")

        # ---- 查询 ----
        elif choice == "8":
            print("\n  回车跳过过滤条件")
            name = input("  厂商名 (回车跳过): ").strip() or None
            model = input("  模型名 (回车跳过): ").strip() or None
            if not name and not model:
                print("  请至少输入一个过滤条件。")
            else:
                query(config, name, model)

        else:
            print("无效选项，请重新选择。")


if __name__ == "__main__":
    main()