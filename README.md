# llm-api-manager

LLM API 配置管理工具 —— 交互式管理多个 LLM 提供商的 API Key 和模型列表。

## 功能

- 添加 / 删除 LLM 提供商（名称、API URL）
- 为每个提供商管理多个 API Key（支持设置过期时间）
- 为每个提供商添加支持的模型列表
- 查询过滤（按厂商名或模型名）
- 配置持久化为 JSON 文件

## 使用方法

### 1. 首次运行自动创建配置文件 `llm_api_configs.json`

```bash
python 202604LLMAPIConfigs.py
```

### 2. 主菜单

```
  1. 查看所有配置
  2. 添加提供商
  3. 为提供商添加 key
  4. 为提供商添加模型
  5. 删除提供商
  6. 删除 key
  7. 删除模型
  8. 查询（按厂商名或模型名过滤）
  0. 保存并退出
  q. 不保存直接退出
```

## 数据文件格式

```json
{
  "providers": [
    {
      "name": "Anthropic",
      "api_url": "https://api.anthropic.com",
      "keys": [
        { "key": "sk-xxx...", "expires": "2026-12-31" }
      ],
      "models": ["claude-opus-4-6", "claude-sonnet-4-6"]
    }
  ]
}
```

## 其他 Python 调用

```python
import json
with open("llm_api_configs.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 查询支持某模型的提供商
providers = [p for p in config["providers"] if "gpt-4o" in p["models"]]
```

## 注意

- `llm_api_configs.json` 包含真实 API Key，**请勿提交到仓库**
- `llm_api_configs.json` 已在 `.gitignore` 中排除
