# 🪙 Solana 资金批量汇总回收脚本

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Solana](https://img.shields.io/badge/Solana-Mainnet-14F195?logo=solana)](https://solana.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **一键归集分散在成百上千个钱包中的零碎 SOL，实现高效率资金结算与集中管理。**

---

## 📌 项目简介

本脚本用于 **Solana 链上多钱包资金的自动归集与回收**（即“汇总账户的资金回收”）。  
只需维护一张包含所有子钱包私钥的表格，运行脚本即可自动将所有符合条件的余额批量转账到您指定的主钱包地址。

**典型应用场景**：  
✅ 交易所用户充值地址资金归集  
✅ 活动奖励钱包余额回收  
✅ DePIN / GameFi 项目方每日佣金结算  
✅ 钱包余额清收与对账

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 📂 批量读取钱包 | 支持从 Excel / CSV 文件中读取大量钱包私钥 |
| 🔍 异步余额查询 | 连接 Solana 主网 RPC，高效查询每个钱包的 SOL 余额，自动扣除手续费 |
| 🎯 智能阈值筛选 | 只对余额 **> 0.00001 SOL** 的钱包执行转账，避免浪费 Gas 费 |
| 🧹 一键归集 | 将所有符合条件的资金批量转账到指定的主钱包地址 |
| 💎 保留最低租金 | 可配置每个钱包保留 `5000 lamports ≈ 0.000005 SOL`，防止账户被回收 |
| 📊 自动生成报告 | 输出 Excel 文件，包含每笔转账的金额、交易签名、状态、时间戳，方便对账 |

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- 一个 Solana 主网 RPC 节点（推荐使用 [Helius](https://dashboard.helius.dev/) 免费套餐）

### 2. 安装依赖

```bash
pip install solders base58 pandas openpyxl aiohttp
3. 获取 RPC API Key（以 Helius 为例）
访问 Helius Dashboard

注册账号并创建 RPC 节点（免费套餐足够使用）

复制你的 API Key

4. 配置文件
在脚本目录下创建或编辑配置文件（或直接修改脚本中的对应变量）：

RPC_API_KEY：替换为你的 Helius API Key

MAIN_WALLET_ADDRESS：替换为你的主钱包地址（资金归集目标）

MIN_BALANCE_THRESHOLD：最小归集阈值（默认 0.00001 SOL）

RENT_EXEMPT_RESERVE：保留余额（默认 5000 lamports）

5. 准备钱包列表
创建 wallets.xlsx 文件，包含一列 private_key（钱包私钥），例如：

private_key
3h...（私钥1）
5j...（私钥2）
6. 运行脚本
bash
python collect.py
脚本将自动执行归集并生成结果文件 result_YYYYMMDD_HHMMSS.xlsx。

📁 输出报告示例
序号	钱包地址	原始余额 (SOL)	转出金额 (SOL)	交易签名	状态	时间
1	7x...	0.0123	0.0122	5x...	✅ 成功	2025-01-15 10:32:21
2	9y...	0.000005	0	—	⏭️ 跳过（低于阈值）	—
⚙️ 高级配置
你可以在脚本头部调整以下参数：

python
# config.py 或 collect.py 顶部
RPC_ENDPOINT = f"https://mainnet.helius-rpc.com/?api-key={RPC_API_KEY}"
MAIN_WALLET = "你的主钱包公钥"
MIN_THRESHOLD_SOL = 0.00001         # 最小归集阈值（SOL）
KEEP_LAMPORTS = 5000                # 每个钱包保留的 lamports（防止账户回收）
MAX_RETRIES = 3                     # 单笔交易失败重试次数
🛠️ 常见问题
Q：为什么需要保留 5000 lamports？
A：Solana 账户需要保持最低租金豁免余额，否则可能被系统回收。保留极小额度既可避免账户丢失，又不影响资金归集效率。

Q：支持同时归集 SPL Token 吗？
A：当前版本仅支持 SOL 归集。如需归集 USDC 等代币，可在此基础上扩展。

Q：交易失败怎么办？
A：脚本内置重试机制，并在最终报告中标记失败记录。可手动检查失败钱包的余额或 RPC 节点状态后重新运行。

