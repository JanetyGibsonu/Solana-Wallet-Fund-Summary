# -Solana-
在 Solana 上，每当你第一次接收一个新代币（比如一个 NFT 或一个 Meme 币）时，系统会自动为你创建一个专门的账户来存放它。为了防止垃圾账户无限占用链上存储资源，创建这个账户时需要一次性存入一笔 SOL 作为“租金”（也叫“免租金最低余额”）。这笔 SOL 会被锁定在该账户中，直到账户被关闭时才会退还。

需要安装以下 Python 依赖包：

bash
pip install solders base58 pandas openpyxl aiohttp
安装建议
建议使用 Python 3.8 及以上版本。

如果安装 solders 遇到编译问题（Windows 上通常有预编译 wheel），可先升级 pip：

bash
pip install --upgrade pip
如果网络慢，可使用国内镜像源，例如：

bash
pip install solders base58 pandas openpyxl aiohttp -i https://pypi.tuna.tsinghua.edu.cn/simple

安装完成后注册账户更改


运行脚本即可：

bash
python collect.py
