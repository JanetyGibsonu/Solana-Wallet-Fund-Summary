<div align="center">

# 🪙 Solana 资金批量归集工具

<p>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://solana.com/"><img src="https://img.shields.io/badge/Solana-Mainnet-14F195?style=for-the-badge&logo=solana&logoColor=black" alt="Solana"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" alt="License"></a>
</p>

**一键归集分散在成百上千个钱包中的零碎 SOL，实现高效率资金结算与集中管理。**

</div>

---

## 📌 项目简介

本工具用于 **Solana 链上多钱包资金的自动归集与回收**。只需维护一张包含所有子钱包私钥的表格，运行脚本即可自动将所有符合条件的余额批量转账到指定的主钱包地址。

**典型应用场景：**

- ✅ 交易所用户充值地址资金归集
- ✅ 活动奖励钱包余额回收
- ✅ DePIN / GameFi 项目方每日佣金结算
- ✅ 钱包余额清收与对账

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📂 批量读取钱包 | 支持从 Excel / CSV 文件中读取大量钱包私钥 |
| 🔍 异步余额查询 | 连接 Solana 主网 RPC，高效并发查询每个钱包的 SOL 余额 |
| 🎯 智能阈值筛选 | 只对余额 `> 0.00001 SOL` 的钱包执行转账，避免浪费 Gas |
| 🧹 一键归集 | 将所有符合条件的资金批量转账到指定主钱包地址 |
| 💎 保留最低租金 | 可配置每个钱包保留 `5000 lamports`，防止账户被系统回收 |
| 📊 自动生成报告 | 输出 Excel 文件，记录每笔转账的金额、签名、状态与时间戳 |

---

## 🚀 快速开始

### 第一步：环境要求

- Python **3.8** 或更高版本
- 一个 Solana 主网 RPC 节点（推荐使用 [Helius](https://dashboard.helius.dev/) 免费套餐）

### 第二步：安装依赖

```bash
pip install solders base58 pandas openpyxl aiohttp
```

### 第三步：获取 RPC API Key

以 [Helius](https://dashboard.helius.dev/) 为例：

1. 注册账号并登录（支持 GitHub / Google）
2. 创建一个新的 RPC 节点（免费套餐即可）
3. 复制你的 API Key，格式类似：`e5a6f7b8-9c0d-4e1f-8a2b-3c4d5e6f7a8b`

```bash
export HELIUS_API_KEY="你复制的 API Key"
```

### 第四步：配置参数

在脚本顶部（或 `config.py`）编辑以下变量：

```python
RPC_ENDPOINT        = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
MAIN_WALLET         = "你的主钱包公钥"
MIN_THRESHOLD_SOL   = 0.00001   # 最小归集阈值（SOL）
KEEP_LAMPORTS       = 5000      # 每个钱包保留的 lamports（防止账户回收）
MAX_RETRIES         = 3         # 单笔交易失败后的重试次数
```

### 第五步：准备钱包列表

创建 `wallets.xlsx` 文件，包含一列 `private_key`：

| private_key |
|-------------|
| 3h...（私钥 1） |
| 5j...（私钥 2） |

### 第六步：运行脚本

```bash
python collect.py
```

脚本将自动执行归集并生成结果文件 `collect_results_YYYYMMDD_HHMMSS.xlsx`。

---

## 📺 运行示例

**控制台输出：**

```
════════════════════════════════════════════════════
       Solana 钱包余额归集工具
════════════════════════════════════════════════════

主钱包地址: 7xKj9yLm3nPq2RsTuVwXyZ1234567890abcdefg
读取到 123 个子钱包私钥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  查询子钱包余额
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  💰 7xKj...3mNp  余额: 0.012345 SOL  |  可转 0.012340 SOL
  ⚠️  9yLm...2qRs  余额: 0.000003 SOL  |  余额过低，跳过
  ❌ 4zWx...7vTb  查询失败: HTTP 429 (Too Many Requests)

📊 查询完成
   总余额:        1.234567 SOL
   可归集:        1.234000 SOL
   有余额子钱包:  45 个

  确认将 45 个子钱包余额归集到主钱包？(yes/no): yes

  ✅ 7xKj...3mNp  转出 0.012340 SOL  sig: 5xLp2Qz1HjK9...
  ✅ 8uYm...9cNq  转出 0.000015 SOL  sig: 3rTp9Xy2...
  ❌ 2qRs...4vWx  转账失败: insufficient lamports for rent exemption

════════════════════════════════════════════════════
  ✅ 归集完成
  本次归集:        0.550000 SOL
  主钱包当前余额:  125.678900 SOL
════════════════════════════════════════════════════
```

**生成的 Excel 报告（`collect_results_20260109_153042.xlsx`）：**

| 钱包地址 | 转出 SOL | 状态 | 交易签名 | 时间 |
|----------|----------|------|----------|------|
| 7xKj...abcdefg | 0.01234 | ✅ 成功 | 5xLp2Qz1... | 2026-01-09 15:30:42 |
| 9yLm...cNp | 0.000015 | ✅ 成功 | 3rTp9Xy2... | 2026-01-09 15:30:45 |
| 2qRs...vWx | 0 | ❌ 失败: insufficient lamports | — | 2026-01-09 15:30:48 |

> 💡 余额低于阈值的钱包不会出现在 Excel 中（仅控制台提示跳过）。如需完整记录，可修改脚本将所有钱包写入报告。

---

## ❓ 常见问题

<details>
<summary><b>Q：为什么需要保留 5000 lamports？</b></summary>

Solana 账户需要保持最低租金豁免余额，否则可能被系统回收。保留极小额度既可避免账户丢失，又不影响资金归集效率。

</details>

<details>
<summary><b>Q：支持同时归集 SPL Token 吗？</b></summary>

当前版本仅支持原生 SOL 归集。如需归集 USDC 等 SPL Token，可在此基础上扩展，欢迎提交 PR。

</details>

<details>
<summary><b>Q：交易失败怎么办？</b></summary>

脚本内置重试机制（默认 3 次），并在最终 Excel 报告中标记失败记录。可手动检查失败钱包的余额或 RPC 节点状态后重新运行。

</details>

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。
