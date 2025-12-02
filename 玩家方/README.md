# 谁是卧底 - 游戏方客户端

## 项目说明

这是"谁是卧底"游戏的游戏方客户端程序，用于与主持方平台进行交互。

## 项目结构

```
玩家方/
├── client.py          # 主程序入口（GUI界面）
├── api_client.py      # API通信模块
├── game_strategy.py   # 游戏策略模块
├── requirements.txt   # 依赖包
└── README.md          # 本文件
```

## 安装依赖

```bash
pip install -r Requirements.txt
```

## 运行方式

### 方式1：直接运行主程序
```bash
python client.py
```

### 方式2：在PyCharm中运行
1. 打开PyCharm，打开本项目
2. 右键点击 `client.py`
3. 选择 "Run 'client'"

## 配置说明

在运行前，需要配置主持方服务器的IP地址：

- 编辑 `api_client.py` 中的 `BASE_URL` 变量
- 或通过GUI界面输入服务器地址

## 功能特性

- ✅ 组名注册
- ✅ 词语接收和展示
- ✅ 描述提交（含时间限制）
- ✅ 投票提交
- ✅ 状态轮询
- ✅ 游戏策略实现
- ✅ 异常上报

## 注意事项

1. 确保主持方服务器已启动（运行 `平台方/backend.py`）
2. 确保网络连接正常，能够访问主持方服务器IP
3. 描述提交需在3秒内完成（题目要求）
4. 状态轮询频率建议2-3秒一次

