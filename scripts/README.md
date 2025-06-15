# 数据库管理说明

本项目使用SQLite数据库存储情感标注数据和用户排序信息，提供更好的数据管理和查询性能。

## 文件说明

- `init_db.py` - 数据库初始化脚本，创建核心表结构
- `user_order_manager.py` - 用户排序数据管理脚本，创建和管理用户排序表
- `manage_db.py` - 数据库管理脚本，用于查看和管理数据库内容

## 项目初始化（首次运行）

### 1. 初始化核心数据库

```bash
python scripts/init_db.py
```

这个命令会：
- 创建 `database/emotion_labels.db` 数据库文件
- 创建 `emotion_labels` 表（情感标注数据）
- 创建 `database/users.db` 用户数据库
- 创建必要的索引和触发器

### 2. 初始化用户排序功能（可选）

```bash
# 创建用户排序相关表
python scripts/user_order_manager.py

# 为特定用户初始化排序数据
python scripts/user_order_manager.py init <username>

# 确保用户排序数据存在（登录时使用）
python scripts/user_order_manager.py ensure <username>
```

### 3. 验证数据库创建

```bash
# 查看表结构和记录总数
python scripts/manage_db.py info

# 查看最近的标注记录（默认10条）
python scripts/manage_db.py recent

# 查看最近的20条记录
python scripts/manage_db.py recent 20

# 查看用户统计信息
python scripts/manage_db.py stats
```

## 数据库表结构

### emotion_labels 表（情感标注数据）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| audio_file | TEXT | 音频文件名 |
| speaker | TEXT | 说话人ID |
| username | TEXT | 标注用户名 |
| v_value | REAL | 情感效价值 |
| a_value | REAL | 情感激活值 |
| emotion_type | TEXT | 情感类型（neutral/non-neutral） |
| discrete_emotion | TEXT | 离散情感标签 |
| patient_status | TEXT | 患者状态（patient/non-patient） |
| audio_duration | REAL | 音频时长（秒） |
| va_complete | BOOLEAN | VA标注是否完整 |
| discrete_complete | BOOLEAN | 离散情感标注是否完整 |
| timestamp | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### user_speaker_orders 表（用户说话人排序）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| username | TEXT | 用户名 |
| speaker_order | TEXT | 说话人排序（JSON格式） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### user_audio_orders 表（用户音频文件排序）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键，自增 |
| username | TEXT | 用户名 |
| speaker | TEXT | 说话人ID |
| audio_order | TEXT | 音频文件排序（JSON格式） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 项目启动

数据库初始化完成后，可以启动应用：

```bash
python start_server.py
```

## 用户排序功能说明

### 自动初始化
- 用户首次登录时，系统会自动检查并创建排序数据
- 默认说话人列表：["spk182", "spk183", "spk184", "spk185", "spk186"]
- 每个说话人的音频排序初始为空列表

### 手动管理
```bash
# 为新用户手动初始化排序数据
python scripts/user_order_manager.py init username

# 确保用户排序数据存在
python scripts/user_order_manager.py ensure username
```

## 数据库优势

1. **性能提升**：数据库查询比JSON文件读取更快
2. **数据完整性**：支持事务和约束，确保数据一致性
3. **并发支持**：多用户同时标注时更安全
4. **查询功能**：支持复杂的数据查询和统计
5. **扩展性**：便于后续添加新功能和字段
6. **用户体验**：支持个性化排序，提升标注效率

## 注意事项

- **首次运行**：必须先执行 `python scripts/init_db.py` 初始化数据库
- **数据库位置**：
  - 情感标注数据：`database/emotion_labels.db`
  - 用户数据：`database/users.db`
- **备份建议**：定期备份数据库文件
- **故障恢复**：如遇问题，可删除数据库文件重新初始化
- **Python版本**：使用 `python` 命令而不是 `python3`
- **虚拟环境**：建议在激活的虚拟环境中运行所有命令