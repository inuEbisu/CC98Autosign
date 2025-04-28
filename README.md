# CC98Autosign

这是一个自动为 CC98 论坛用户进行每日签到的 Python 程序。

[![License](https://img.shields.io/static/v1?label=License&message=WTFPL&color=lightrey)](/LICENSE.txt)
[![Build and Release with Nuitka](https://github.com/inuEbisu/CC98Autosign/actions/workflows/release.yml/badge.svg)](https://github.com/inuEbisu/CC98Autosign/actions/workflows/release.yml)

## 功能特点

- 支持多账号批量签到
- 日志记录签到结果
- 支持循环执行模式
- 错误自动重试
- 自动创建示例配置文件
- 支持 WebVPN

## 使用步骤

### 方法一：使用预编译二进制文件

该办法无需安装 Python。

1. 前往 [Releases](https://github.com/inuEbisu/CC98Autosign/releases) 页面
2. 根据你的操作系统下载对应的文件：
   - Windows 用户下载 `CC98Autosign-windows-amd64.exe`
   - Linux 用户下载 `CC98Autosign-linux-amd64`
3. 将下载的文件放在任意目录下
4. 首次运行时会自动创建 `config.json` 文件，只需修改其中的用户名和密码即可

### 方法二：从源码运行

1. 确保你的系统已安装 Python 3.13（3.x 应该都行，不过没测试过）
2. 克隆/下载本项目到本地
3. 安装必要的依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### 方法三：使用 GitHub Actions

该仓库已配置 GitHub Actions，可实现每天早上 8:00 自动签到

出于项目安全性的考虑，checkin.yml 处于停用状态

#### 配置
1. 点击仓库页面右上角的 Use this template 自建仓库（请勿 fork 该仓库）
2. 恢复 ./github/workflows/checkin.yml 的重命名
3. 进入你自己的仓库的 Settings → Secrets → Actions
4. 点击 New repository secret 按钮
5. 添加以下 Secret：

| Secret 名称   | 值内容                                |
|--------------|-------------------------------------|
| CONFIG_DATA  | 完整的 config.json 文件内容（保持JSON格式） |

## 配置说明

程序会在首次运行时自动创建 `config.json` 文件，你只需要修改其中的用户名和密码即可；也支持按照 JSON 格式添加更多的用户账号。配置文件格式如下：

```json
{
   "webvpn": {
      "username": "your_webvpn_username",
      "password": "your_webvpn_password"
   },
   "users": [
      {
         "username": "your_username1",
         "password": "your_password1"
      },
      {
         "username": "your_username2",
         "password": "your_password2"
      }
   ]
}
```

如果不识得 JSON 格式，也可以将这串代码和你的账号密码一并丢给大模型，它会帮你完成。你也可以手动创建或修改 `config.json` 文件。

## 使用方法

### Windows 用户

1. 双击运行 `CC98Autosign.exe`
2. 或使用命令行：
   ```bash
   CC98Autosign.exe
   ```

### Linux 用户

1. 给程序添加执行权限：
   ```bash
   chmod +x CC98Autosign
   ```
2. 运行程序：
   ```bash
   ./CC98Autosign
   ```

### Python 源码运行

```bash
python main.py
```

这将执行一次签到操作，完成后程序自动退出。

### 循环执行模式

如果你希望程序每小时自动执行一次签到（适合在服务器上运行），可以使用 `--loop` 参数：

```bash
CC98Autosign.exe --loop  # Windows
./CC98Autosign --loop  # Linux
python main.py --loop  # Python
```

### Crontab

对于 Linux 用户，可以使用 `crontab` 来统一管理计划任务：

```bash
crontab -e
```

增加一行：
```
0 8 * * * cd (config.json所在目录) && (CC98Autosign可执行文件的路径)
```

> `0 8 * * *` 是一个 Cron 表达式，用于指定定时任务的执行时间。更多信息详见 [Cron](https://en.wikipedia.org/wiki/Cron)

### 程序输出说明

程序运行时会显示以下信息：
- 登录状态
- 签到结果
- 上次签到时间
- 获得的财富值
- 连续签到天数
- 错误信息（如果有）

## 注意事项

- 请妥善保管你的账号密码，分发程序时不要将 `config.json` 文件也分享给他人了
- 如果遇到网络问题，程序会自动等待 10 秒后重试
- 可以通过 Ctrl+C 随时终止程序运行
- 预编译版本无需安装 Python 环境，但仍要记得正确配置 `config.json` 文件

## 常见问题

1. **登录失败**
   - 检查用户名和密码是否正确（自动创建的 `config.json` 记得修改）
   - 确认网络连接正常
   - 检查是否是校内网，CC98 网站是否可以正常访问

2. **签到失败**
   - 可能是今天已经签到过
   - 可能是网络问题，程序会自动重试

3. **程序无法运行**
   - Windows 用户：确保下载的是对应系统版本的 exe 文件
   - Linux 用户：确保已添加执行权限
   - 如果使用预编译版本，确保 `config.json` 文件与程序在同一目录下

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

### 提交规范

本项目使用[约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)规范。

### 开发环境配置

为了确保代码风格和格式的一致性，本项目使用了 pre-commit 工具链。贡献者 clone 仓库后，需要手动安装 pre-commit 并执行以下命令启用：

```bash
pip install pre-commit
pre-commit install
```

这样，每次 commit 时 pre-commit 会自动运行检查。

### 贡献者列表
<a href="https://github.com/inuEbisu/CC98Autosign/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=inuEbisu/CC98Autosign" />
</a>

## License

This project is licensed under the WTFPL.
