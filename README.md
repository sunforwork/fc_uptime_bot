# FC Uptime Bot
阿里云边缘函数 - 网站监控机器人

## 功能特性

- 支持多种监控类型：HTTP、HTTPS、TCP端口检测
- 支持监控URL、IP地址、域名
- 自动生成带时间戳的JSON结果文件
- 自动推送监控结果到GitHub仓库
- 完全基于Python标准库，无外部依赖

## 使用方法

### 1. 配置监控站点

编辑 `site.json` 文件，添加需要监控的站点：

```json
{
  "sites": [
    {
      "name": "站点名称",
      "url": "https://example.com",
      "type": "https",
      "timeout": 10
    },
    {
      "name": "TCP端口检测",
      "url": "example.com",
      "type": "tcp",
      "port": 443,
      "timeout": 5
    }
  ]
}
```

### 2. 部署到阿里云FC

将 `index.py` 和 `site.json` 上传到阿里云Function Compute，设置入口函数为 `index.handler`。

### 3. 监控结果

- 监控结果将自动推送到GitHub仓库：`sunforwork/uptime_page`
- 文件名格式：`uptime-YYYY-MM-DDTHH-MM-SS-mmmmmm.json`
- 包含每个站点的状态、响应时间、错误信息等

## 配置选项

### 站点配置参数

- `name`: 站点名称（必需）
- `url`: 监控地址（必需）
- `type`: 监控类型 - `http`、`https`、`tcp`（必需）
- `timeout`: 超时时间（秒，可选，默认10秒）
- `port`: TCP端口号（TCP类型时需要，默认80）

### 监控类型说明

- **HTTP/HTTPS**: 发送HTTP请求检查响应状态码
- **TCP**: 检查TCP端口连通性

## 本地测试

```bash
python3 index.py
```

运行本地测试脚本：

```bash
python3 test_local.py
```
