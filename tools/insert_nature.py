# tools/init_nature_db.py
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "omnipilot",
    "password": "omnipilot123",
    "database": "omnipilot"
}

SQL_CREATE_NATURES_TABLE = """
-- 重新创建性格表（先删除旧表再建新表）
DROP TABLE IF EXISTS natures CASCADE;
CREATE TABLE natures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    increased_stat VARCHAR(10),   -- 增益属性（攻击/防御/魔攻/魔抗/速度/生命）
    decreased_stat VARCHAR(10)    -- 减益属性
);
"""

SQL_INSERT_NATURES = """
INSERT INTO natures (name, increased_stat, decreased_stat) VALUES
('开朗', '速度', '魔攻'),
('平和', '生命', '魔攻'),
('固执', '攻击', '魔攻'),
('胆小', '速度', '攻击'),
('莽撞', '速度', '魔抗'),
('粗心', '生命', '魔攻'),
('忧郁', '生命', '防御'),
('大胆', '攻击', '防御'),      -- 注意：这里按你提供的数据，如需修改请替换
('热情', '速度', '生命'),
('调皮', '攻击', '魔抗'),
('踏实', '生命', '速度'),
('急躁', '速度', '防御'),
('天真', '防御', '魔攻'),
('沉默', '生命', '攻击'),
('逞强', '攻击', '生命'),
('勇敢', '攻击', '速度'),
('害羞', '魔抗', '魔攻'),
('坦率', '防御', '生命'),
('稳重', '防御', '攻击'),
('温顺', '魔抗', '防御'),
('偏执', '魔攻', '魔抗'),
('慎重', '魔抗', '速度'),
('专注', '魔攻', '防御'),
('懒散', '防御', '魔抗'),
('悠闲', '防御', '速度'),
('冷静', '魔攻', '速度'),
('焦虑', '魔抗', '生命'),
('理智', '魔攻', '生命'),
('警惕', '魔抗', '攻击'),
('聪明', '魔攻', '攻击');
"""

def init_nature_database():
    print("正在连接 PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    print("重建性格表...")
    cursor.execute(SQL_CREATE_NATURES_TABLE)

    print("插入30种性格数据...")
    cursor.execute(SQL_INSERT_NATURES)

    cursor.close()
    conn.close()
    print("✅ 性格数据初始化完成！")

if __name__ == "__main__":
    init_nature_database()