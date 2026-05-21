import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "omnipilot",
    "password": "omnipilot123",
    "database": "omnipilot"
}

def test_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. 总数
    cursor.execute("SELECT COUNT(*) FROM pokemon;")
    total = cursor.fetchone()[0]
    print(f"📊 精灵总数：{total}\n")

    # 2. 列出所有精灵基本信息（按编号排序）
    cursor.execute("""
        SELECT national_number, name, primary_type, secondary_type, species_total, ability
        FROM pokemon
        ORDER BY national_number;
    """)
    print("=" * 100)
    print("精灵基本信息：")
    print("=" * 100)
    for row in cursor.fetchall():
        num, name, ptype, stype, total, ability = row
        stype_str = stype if stype else "无"
        print(f"{num}\t{name}\t{ptype}\t{stype_str}\t种族值: {total}\t特性: {ability}")

    # 3. 查看种族值详情（联合查询）
    print("\n" + "=" * 100)
    print("精灵种族值详情：")
    print("=" * 100)
    cursor.execute("""
        SELECT p.national_number, p.name,
               s.hp, s.attack, s.defense, s.sp_attack, s.sp_defense, s.speed
        FROM pokemon p
        JOIN pokemon_stats s ON p.id = s.pokemon_id
        ORDER BY p.national_number;
    """)
    for row in cursor.fetchall():
        num, name, hp, atk, df, spa, spd, spe = row
        print(f"{num} {name} | HP:{hp} 物攻:{atk} 物防:{df} 魔攻:{spa} 魔防:{spd} 速度:{spe}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_database()