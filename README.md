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
