# 数据库迁移说明

本项目已从JSON文件存储迁移到SQLite数据库存储，以提供更好的数据管理和查询性能。

## 文件说明

- `init_db.py` - 数据库初始化脚本，创建表结构并迁移现有JSON数据
- `manage_db.py` - 数据库管理脚本，用于查看和管理数据库内容
- `emotion_labels.db` - SQLite数据库文件（位于labels目录下）

## 使用方法

### 1. 初始化数据库

```bash
python3 scripts/init_db.py
```

这个命令会：
- 创建SQLite数据库和表结构
- 自动迁移现有的JSON标注数据到数据库
- 保留原有的JSON文件作为备份

### 2. 查看数据库信息

```bash
# 查看表结构和记录总数
python3 scripts/manage_db.py info

# 查看最近的标注记录（默认10条）
python3 scripts/manage_db.py recent

# 查看最近的20条记录
python3 scripts/manage_db.py recent 20

# 查看用户统计信息
python3 scripts/manage_db.py stats
```

## 数据库表结构

### emotion_labels 表

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
| play_count | INTEGER | 播放次数 |
| va_complete | BOOLEAN | VA标注是否完整 |
| discrete_complete | BOOLEAN | 离散情感标注是否完整 |
| timestamp | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 兼容性说明

- 系统会自动检测SQLite3模块的可用性
- 如果SQLite3不可用，系统会自动回退到JSON文件存储
- 现有的JSON文件会被保留作为备份
- 数据库和JSON文件可以并存，系统优先使用数据库

## 优势

1. **性能提升**：数据库查询比JSON文件读取更快
2. **数据完整性**：支持事务和约束，确保数据一致性
3. **并发支持**：多用户同时标注时更安全
4. **查询功能**：支持复杂的数据查询和统计
5. **扩展性**：便于后续添加新功能和字段

## 注意事项

- 首次运行需要执行数据库初始化
- 数据库文件位于 `database/emotion_labels.db`
- 建议定期备份数据库文件
- 如遇到问题，可以删除数据库文件重新初始化