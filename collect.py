"""
Solana 钱包余额查询 + 归集工具
功能：
  1. 从 Excel/CSV 读取私钥列表
  2. 查询每个钱包余额
  3. 将余额归集到主钱包（保留最低租金豁免）

安装依赖: pip install solders base58 pandas openpyxl aiohttp
运行:     python collect.py
"""

import asyncio
import sys
import base64
import json
from datetime import datetime

import aiohttp
import base58
import pandas as pd
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer as sol_transfer
from solders.transaction import Transaction
from solders.hash import Hash

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ─── 配置区 ───────────────────────────────────────────────────────────────────
CONFIG = {
    # RPC 节点，推荐 Helius 免费节点
    "RPC_URL": "https://mainnet.helius-rpc.com/?api-key=填入https://dashboard.helius.dev/的kye",

    # 私钥文件（Excel 或 CSV）
    "EXCEL_FILE": "wallets.xlsx",

    # 私钥列名
    "PRIVATE_KEY_COLUMN": "私钥",

    # 主钱包私钥（Base58），归集目标
    "MAIN_WALLET_KEY": "填写你的主钱包私钥",

    # 每个钱包保留的最低 lamports（Solana 账户最低要求约 890880）
    # 设为 0 则尝试转走全部（账户可能被系统回收，一般无影响）
    "KEEP_LAMPORTS": 5000,

    # 最小归集金额（lamports），低于此不转账，避免 gas 浪费
    "MIN_TRANSFER": 10000,

    # 请求间隔（秒）
    "DELAY": 1.0,
}

LAMPORTS_PER_SOL = 1_000_000_000
# ─────────────────────────────────────────────────────────────────────────────


def load_keypair(raw: str) -> Keypair:
    raw = str(raw).strip()
    try:
        return Keypair.from_bytes(base58.b58decode(raw))
    except Exception:
        pass
    try:
        return Keypair.from_bytes(bytes(json.loads(raw)))
    except Exception:
        pass
    raise ValueError(f"无法解析私钥: {raw[:12]}...")


def load_wallets(filepath: str, column: str) -> list[str]:
    import os
    if not os.path.exists(filepath):
        print(f"❌ 找不到文件: {filepath}")
        sys.exit(1)

    if filepath.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(filepath)
    else:
        for enc in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                df = pd.read_csv(filepath, encoding=enc)
                break
            except UnicodeDecodeError:
                continue

    # 自动适配列名
    if column not in df.columns:
        for alt in ['privateKey', 'private_key', 'PrivateKey', 'key']:
            if alt in df.columns:
                df = df.rename(columns={alt: column})
                break
        else:
            if len(df.columns) == 1:
                df.columns = [column]
            else:
                raise ValueError(f'找不到列 "{column}"，现有列: {list(df.columns)}')

    return df[column].dropna().astype(str).str.strip().tolist()


class Collector:
    def __init__(self):
        self.rpc_url = CONFIG["RPC_URL"]

    async def rpc(self, method: str, params=None) -> dict:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.post(
                        self.rpc_url, json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as r:
                        data = await r.json()
                        if "error" in data:
                            raise Exception(data["error"])
                        return data
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

    async def get_balance(self, pubkey: Pubkey) -> int:
        res = await self.rpc("getBalance", [str(pubkey)])
        return res["result"]["value"]

    async def get_blockhash(self) -> Hash:
        res = await self.rpc("getLatestBlockhash")
        return Hash.from_string(res["result"]["value"]["blockhash"])

    async def send_tx(self, tx: Transaction) -> str:
        encoded = base64.b64encode(bytes(tx)).decode()
        res = await self.rpc("sendTransaction", [
            encoded,
            {"encoding": "base64", "preflightCommitment": "confirmed"}
        ])
        return res["result"]

    async def transfer(self, from_kp: Keypair, to: Pubkey, lamports: int) -> str:
        bh = await self.get_blockhash()
        ix = sol_transfer(TransferParams(
            from_pubkey=from_kp.pubkey(), to_pubkey=to, lamports=lamports
        ))
        tx = Transaction.new_signed_with_payer([ix], from_kp.pubkey(), [from_kp], bh)
        return await self.send_tx(tx)

    async def run(self):
        print("═" * 52)
        print("       Solana 钱包余额归集工具")
        print("═" * 52)

        if not CONFIG["MAIN_WALLET_KEY"]:
            print("❌ 请先在 CONFIG 中填入 MAIN_WALLET_KEY（主钱包私钥）")
            sys.exit(1)

        main_kp = load_keypair(CONFIG["MAIN_WALLET_KEY"])
        main_addr = str(main_kp.pubkey())
        print(f"\n主钱包: {main_addr}")

        # 读取钱包列表
        raw_keys = load_wallets(CONFIG["EXCEL_FILE"], CONFIG["PRIVATE_KEY_COLUMN"])
        print(f"读取到 {len(raw_keys)} 个钱包\n")

        wallets: list[Keypair] = []
        for raw in raw_keys:
            try:
                kp = load_keypair(raw)
                # 跳过主钱包本身
                if str(kp.pubkey()) != main_addr:
                    wallets.append(kp)
            except Exception as e:
                print(f"  ⚠️  跳过无效私钥: {e}")

        # ── 查询余额 ──────────────────────────────────────────────────────────
        print(f"{'━'*52}")
        print("  查询钱包余额")
        print(f"{'━'*52}\n")

        wallet_info = []
        total_balance = 0
        total_transferable = 0

        for kp in wallets:
            addr = str(kp.pubkey())
            short = f"{addr[:8]}...{addr[-6:]}"
            try:
                bal = await self.get_balance(kp.pubkey())
                # 扣除一笔转账的 gas（约 5000 lamports），剩余全部转走
                transferable = max(0, bal - 5000)
                total_balance += bal
                total_transferable += transferable

                status = f"可转 {transferable/LAMPORTS_PER_SOL:.6f} SOL" if transferable > CONFIG["MIN_TRANSFER"] else "余额过低跳过"
                print(f"  💰 {short}  余额: {bal/LAMPORTS_PER_SOL:.6f} SOL  |  {status}")
                wallet_info.append({"kp": kp, "balance": bal, "transferable": transferable})
            except Exception as e:
                print(f"  ❌ {short}  查询失败: {e}")
                wallet_info.append({"kp": kp, "balance": 0, "transferable": 0})
            await asyncio.sleep(CONFIG["DELAY"])

        to_transfer = [w for w in wallet_info if w["transferable"] > CONFIG["MIN_TRANSFER"]]

        print(f"\n📊 查询完成")
        print(f"   总余额:     {total_balance/LAMPORTS_PER_SOL:.6f} SOL")
        print(f"   可归集:     {total_transferable/LAMPORTS_PER_SOL:.6f} SOL")
        print(f"   有余额钱包: {len(to_transfer)} 个\n")

        if not to_transfer:
            print("✅ 没有可归集的余额，程序结束。")
            return

        # ── 确认并归集 ────────────────────────────────────────────────────────
        confirm = input(f"  确认将 {len(to_transfer)} 个钱包余额归集到主钱包？(yes/no): ").strip().lower()
        if confirm not in ("yes", "y"):
            print("\n已取消。")
            return

        print()
        results = []
        grand_total = 0

        for w in to_transfer:
            kp: Keypair = w["kp"]
            addr = str(kp.pubkey())
            short = f"{addr[:8]}...{addr[-6:]}"
            lamports = w["transferable"]

            try:
                sig = await self.transfer(kp, main_kp.pubkey(), lamports)
                grand_total += lamports
                print(f"  ✅ {short}  转出 {lamports/LAMPORTS_PER_SOL:.6f} SOL  sig: {sig[:16]}...")
                results.append({
                    "钱包": addr,
                    "转出SOL": lamports / LAMPORTS_PER_SOL,
                    "状态": "成功",
                    "交易签名": sig,
                    "时间": datetime.now().isoformat(),
                })
            except Exception as e:
                print(f"  ❌ {short}  转账失败: {e}")
                results.append({
                    "钱包": addr,
                    "转出SOL": 0,
                    "状态": f"失败: {e}",
                    "交易签名": "",
                    "时间": datetime.now().isoformat(),
                })

            await asyncio.sleep(CONFIG["DELAY"])

        # 保存结果
        if results:
            df = pd.DataFrame(results)
            out = f"collect_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(out, index=False)
            print(f"\n📊 结果已保存: {out}")

        final = await self.get_balance(main_kp.pubkey())
        print(f"\n{'═'*52}")
        print(f"  ✅ 归集完成")
        print(f"  本次归集:       {grand_total/LAMPORTS_PER_SOL:.6f} SOL")
        print(f"  主钱包当前余额: {final/LAMPORTS_PER_SOL:.6f} SOL")
        print(f"{'═'*52}\n")


async def main():
    await Collector().run()

if __name__ == "__main__":
    asyncio.run(main())
