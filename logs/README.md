# 日志目录

此目录用于存储系统运行日志文件。

## 日志文件类型

- `face_unlock_YYYYMMDD.log` - 主系统日志
- `events_YYYYMMDD.log` - 事件日志
- `recognition_YYYYMMDD.log` - 识别结果日志

## 日志配置

日志配置在 `config.json` 中的 `system` 部分：

- `log_level`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `log_dir`: 日志目录路径
- `max_log_size_mb`: 单个日志文件最大大小
- `log_rotation_count`: 保留的日志文件数量

## 注意事项

- 日志文件会自动轮转以防止磁盘空间耗尽
- 个人敏感信息不会记录在日志中
- 可通过 `sudo journalctl -u face-unlock-web` 查看系统服务日志
