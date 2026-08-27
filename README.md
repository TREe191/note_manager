# Personal Note Manager

一个面向初学者的 Python 个人笔记管理器，提供命令行和 PySide6 桌面图形界面。项目使用本地 SQLite 保存数据，适合练习需求拆分、分层设计、测试和基础软件开发流程。

## V1.3 当前功能

- 创建笔记：输入标题、正文和可选标签后保存笔记。
- 查看笔记列表：展示笔记编号、标题、标签和更新时间。
- 查看笔记详情：按笔记编号查看标题、正文、标签、创建时间和更新时间。
- 编辑笔记：按编号修改标题、正文和标签，并更新修改时间。
- 删除笔记：按编号选择笔记，确认后删除并保存数据。
- 搜索笔记：按关键词搜索标题、正文和标签，并按标签匹配程度和更新时间排序。
- CLI：支持分层菜单、列表和搜索结果直达详情，以及详情页内编辑和删除。
- PySide6 GUI：支持笔记浏览、新建、查看、编辑、删除和搜索。
- SQLite 持久化：程序默认读写 `data/notes.db`。
- 自动迁移：首次启动时，如存在旧 `data/notes.json` 且尚未创建 `notes.db`，会自动迁移笔记数据。
- `unittest` 测试：覆盖业务逻辑、JSON/SQLite 存储、迁移、CLI 和 GUI 关键流程。

## 安装依赖

在项目根目录运行：

```powershell
python -m pip install -r requirements.txt
```

## 运行方式

命令行界面：

```powershell
python main.py
```

桌面图形界面：

```powershell
python main_gui.py
```

程序默认读写 `data/notes.db`。旧的 `data/notes.json` 只会在首次迁移时读取，迁移成功后会保留原文件作为备份，不会被删除或覆盖。

## 测试方式

在项目根目录运行：

```powershell
python -m unittest discover -s tests -v
```

测试使用临时数据文件，不会修改真实笔记数据。

## 项目结构

```text
note_manager/
├─ main.py                 # 命令行界面入口
├─ main_gui.py             # PySide6 图形界面入口
├─ requirements.txt        # Python 依赖
├─ data/
│  ├─ notes.db             # 默认 SQLite 笔记数据
│  └─ notes.json           # 旧 JSON 数据迁移备份
├─ src/
│  ├─ models.py            # 笔记数据模型和字段清理规则
│  ├─ storage.py           # 存储接口和 JSON 存储实现
│  ├─ sqlite_storage.py    # SQLite 存储实现
│  ├─ migration.py         # JSON 到 SQLite 的首次迁移
│  ├─ note_service.py      # 创建、查询、编辑、删除、搜索等业务逻辑
│  ├─ cli.py               # 命令行菜单、输入和结果展示
│  └─ gui/                 # PySide6 窗口、控制器和样式
├─ tests/
│  ├─ test_note_service.py # 业务逻辑测试
│  ├─ test_storage.py      # JSON 存储测试
│  ├─ test_sqlite_storage.py # SQLite 存储测试
│  ├─ test_migration.py    # 数据迁移测试
│  ├─ test_cli.py          # 命令行交互测试
│  └─ test_gui_*.py        # GUI 控制器与窗口测试
├─ .gitignore              # Git 忽略规则
└─ README.md               # 项目说明
```
