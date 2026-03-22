# 番茄钟工作台

一个基于 Python + PyQt6 的本地番茄钟时间追踪工具。

## 功能特性

### 任务管理
- 新建、编辑、归档、删除任务
- 预估番茄数与完成进度追踪
- 全文搜索任务标题和备注，关键词高亮

### 番茄钟计时
- 工作/休息循环计时（默认：工作25分钟，短休息5分钟，长休息15分钟）
- 可配置循环次数（每4个番茄后长休息）
- 支持暂停、恢复、跳过、重置
- 自动开始下一阶段（可选）

### 视图切换
- 任务管理视图
- 统计分析视图
- 分屏视图（三栏同时显示）

### 统计分析
- 每日/每周专注时长统计
- 图表可视化展示
- 生产力评分

### 数据导出
- 导出 CSV 统计报告
- 导出 PDF 周报/日报

### 系统集成
- 系统托盘控制（开始、暂停、跳过、显示窗口）
- 桌面通知提醒
- 可选声音提醒
- 窗口状态持久化

## 技术栈

- **GUI**: PyQt6
- **数据库**: SQLite
- **计时**: QTimer
- **PDF导出**: Qt 打印模块
- **配置存储**: QSettings

## 项目结构

```
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── src/
│   ├── app/               # 主窗口、界面组件
│   │   ├── main_window.py
│   │   ├── timer_display.py
│   │   ├── task_list.py
│   │   ├── search_widget.py
│   │   └── settings_dialog.py
│   ├── timer/             # 计时逻辑
│   │   ├── pomodoro_timer.py
│   │   └── qt_timer.py
│   ├── analytics/         # 统计与导出
│   │   ├── stats_calculator.py
│   │   ├── charts.py
│   │   ├── csv_exporter.py
│   │   └── pdf_exporter.py
│   ├── storage/           # 数据存储
│   │   ├── database.py
│   │   ├── models.py
│   │   └── settings.py
│   └── system/            # 系统集成
│       ├── tray_icon.py
│       └── notifications.py
└── tests/                 # 测试用例
```

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 使用说明

1. **新建任务**: 点击"新建任务"按钮，输入标题和预估番茄数
2. **关联任务**: 在计时器下拉框选择任务，或双击任务列表中的任务
3. **开始计时**: 点击"开始"按钮启动番茄钟
4. **完成番茄**: 倒计时结束后自动记录，进入休息阶段
5. **查看统计**: 切换到"统计分析"标签页查看图表
6. **导出报告**: 菜单 → 文件 → 导出 → 选择 CSV 或 PDF

## 测试

```bash
pytest
```

测试覆盖：
- 计时状态机与边界时间
- 任务 CRUD 操作
- 统计聚合计算
- 搜索匹配与高亮
- 导出功能
- 窗口状态存取

## 许可证

MIT License
