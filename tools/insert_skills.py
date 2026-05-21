# tools/init_skill_db.py
# 插入精灵技能到数据库
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "omnipilot",
    "password": "omnipilot123",
    "database": "omnipilot"
}

SQL_CREATE_SKILL_TABLES = """
-- 技能表
CREATE TABLE IF NOT EXISTS moves (
    id SERIAL PRIMARY KEY,
    move_number VARCHAR(10) NOT NULL UNIQUE,      -- 技能编号，如 "001"
    name VARCHAR(50) NOT NULL,
    function_type VARCHAR(10) NOT NULL CHECK (function_type IN ('攻击', '防御', '状态')),
    power INTEGER,                               -- 威力，变化技能可为NULL
    energy_cost INTEGER,                         -- 能耗（PP或能量）
    category VARCHAR(10) NOT NULL CHECK (category IN ('物理', '魔法', '变化')),
    description TEXT
);

-- 精灵可学技能关联表
CREATE TABLE IF NOT EXISTS pokemon_moves (
    pokemon_id INTEGER NOT NULL REFERENCES pokemon(id) ON DELETE CASCADE,
    move_id INTEGER NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
    learn_method VARCHAR(20) NOT NULL CHECK (learn_method IN ('升级', '技能机', '遗传')),
    level_learned INTEGER,                        -- 升级习得时的等级
    PRIMARY KEY (pokemon_id, move_id, learn_method)
);

-- 索引：加快按精灵ID和技能ID的查询
CREATE INDEX IF NOT EXISTS idx_pokemon_moves_pokemon ON pokemon_moves(pokemon_id);
CREATE INDEX IF NOT EXISTS idx_pokemon_moves_move ON pokemon_moves(move_id);
"""

# 示例插入语句（实际使用时取消注释并补充数据）
SQL_INSERT_EXAMPLE_MOVES = """
-- 示例技能，后期可逐条添加
-- INSERT INTO moves (move_number, name, function_type, power, energy_cost, category, description) VALUES
-- ('001', '光芒四射', '攻击', 80, 10, '魔法', '发射耀眼的光芒攻击对手，一定概率降低对手命中率。'),
-- ('002', '暗影突袭', '攻击', 90, 15, '物理', '用暗影包裹身体撞击对手，容易击中要害。');
"""

def init_skill_database():
    print("正在连接 PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    print("创建技能相关表...")
    cursor.execute(SQL_CREATE_SKILL_TABLES)

    # 如果以后需要插入初始数据，取消注释下一行
    # print("插入示例技能...")
    # cursor.execute(SQL_INSERT_EXAMPLE_MOVES)

    cursor.close()
    conn.close()
    print("✅ 技能数据库初始化完成！")

if __name__ == "__main__":
    init_skill_database()