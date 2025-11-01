# Arkain.io 自动签到系统

这是一个基于GitHub Actions的Arkain.io全自动签到系统，使用Python Selenium库实现浏览器自动化，完美支持JavaScript渲染和复杂登录流程。

## 功能特性

- ✅ 全自动登录Arkain.io账户
- ✅ 智能签到功能，支持多种按钮类型
- ✅ Telegram通知支持
- ✅ GitHub Actions自动调度
- ✅ 真实浏览器环境，完美模拟用户操作
- ✅ 错误处理和日志记录
- ✅ 多区域服务器支持
- ✅ 支持JavaScript渲染和动态内容加载

## 环境变量配置

在GitHub仓库的Settings > Secrets and variables > Actions中添加以下secrets：

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `ARKAIN_EMAIL` | Arkain.io登录邮箱 | ✅ |
| `ARKAIN_PASSWORD` | Arkain.io登录密码 | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram机器人token (可选) | ❌ |
| `TELEGRAM_CHAT_ID` | Telegram聊天ID (可选) | ❌ |

### Telegram通知设置（可选）

1. 创建Telegram机器人：与 @BotFather 对话创建新机器人
2. 获取Bot Token
3. 获取Chat ID：与机器人对话发送消息后访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

### 本地测试

#### 环境要求

- Python 3.8+
- uv (推荐的Python包管理器)
- Google Chrome浏览器

#### 安装依赖

```bash
# 安装uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### 安装Chrome浏览器

```bash
# Ubuntu/Debian系统
sudo apt-get update
sudo apt-get install -y wget gnupg unzip curl
sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

#### 运行测试

```bash
# 设置环境变量
export ARKAIN_EMAIL="your_email@example.com"
export ARKAIN_PASSWORD="your_password"
export TELEGRAM_BOT_TOKEN="your_bot_token"  # 可选
export TELEGRAM_CHAT_ID="your_chat_id"      # 可选

# 运行签到脚本
source .venv/bin/activate
python arkain_checkin.py
```

## GitHub Actions配置

系统已配置为每天UTC时间00:30自动运行，也可以手动触发。

### 调度时间

- 自动运行：每天 UTC 00:30 (北京时间 08:30)
- 手动触发：在Actions页面手动运行

## 工作原理

1. **浏览器自动化**：使用Selenium控制Chrome浏览器进行真实用户操作模拟
2. **智能登录**：自动识别多种登录表单格式，支持复杂认证流程
3. **签到检测**：智能检测"Daily check-in"按钮，支持动态加载内容
4. **JavaScript支持**：完美处理JavaScript渲染的页面和AJAX请求
5. **多区域支持**：自动尝试多个Arkain服务器区域
6. **错误处理**：完善的异常处理和日志记录
7. **通知系统**：成功/失败时发送Telegram通知

## 支持的服务器区域

- account.arkain.io (主账户系统)
- arkain.io (控制台)
- ap-south-1.arkain.io (亚太南部)
- ap-northeast-2.arkain.io (亚太东北)
- us-west-2.arkain.io (美国西部)
- eu-central-1.arkain.io (欧洲中部)

## 日志示例

```
2025-11-01 22:28:36,906 - INFO - ===============================================
2025-11-01 22:28:36,906 - INFO - Arkain.io 自动签到脚本启动
2025-11-01 22:28:36,906 - INFO - 时间: 2025-11-01 22:28:36
2025-11-01 22:28:36,906 - INFO - ===============================================
2025-11-01 22:28:36,906 - INFO - 开始登录Arkain账户...
2025-11-01 22:28:37,696 - INFO - 发送登录请求...
2025-11-01 22:28:37,888 - INFO - 登录成功
2025-11-01 22:28:37,888 - INFO - 导航到仪表板...
2025-11-01 22:28:38,447 - INFO - 尝试访问仪表板: https://account.arkain.io/dashboard
2025-11-01 22:28:39,342 - INFO - 成功到达仪表板
2025-11-01 22:28:39,342 - INFO - 开始执行签到...
2025-11-01 22:28:46,533 - INFO - 签到操作完成（无明确结果提示）
2025-11-01 22:28:46,533 - INFO - ✅ Arkain.io 签到成功
```

## 故障排除

### 常见问题

1. **登录失败**：检查邮箱密码是否正确
2. **无法访问仪表板**：可能是服务器维护或网络问题
3. **签到失败**：可能已经签到过或签到功能暂时不可用

### 调试模式

查看GitHub Actions运行日志获取详细错误信息。

## 安全说明

- ✅ 密码存储在GitHub Secrets中，安全可靠
- ✅ 使用HTTPS加密传输
- ✅ 不会在日志中显示敏感信息
- ✅ 代码开源，无恶意功能

## 更新日志

### v3.0.0
- 🔄 迁移到Selenium浏览器自动化
- 🌐 完美支持JavaScript渲染和动态内容
- 🎯 增强登录检测：支持多种登录表单格式
- 🚀 真实浏览器环境：完美模拟用户操作
- 🔍 智能元素检测：支持动态加载的签到按钮
- 📈 大幅提升成功率：解决复杂认证流程问题

### v2.1.0
- 🎯 优化签到检测：专门针对"Daily check-in"按钮
- 🚀 直接签到：登录成功后直接在主页面查找签到功能
- 🔍 增强模式匹配：支持更多签到按钮格式
- 📈 提升成功率：减少不必要的页面跳转

### v2.0.0
- 🔄 从Selenium迁移到requests库
- 🚀 移除浏览器依赖，提升性能
- 🛡️ 增强安全性和稳定性
- 🌍 支持更多服务器区域
- 📝 改进日志记录和错误处理

### v1.0.0
- 🎉 初始版本，基于Selenium实现

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License - 详见LICENSE文件

## 免责声明

本工具仅供学习和研究使用，请遵守Arkain.io的服务条款。使用本工具所产生的任何后果由用户自行承担。