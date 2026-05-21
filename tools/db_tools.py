# tools/db_tools.py
"""数据库查询工具：根据属性查找精灵"""
from tools.sql_executor import default_executor

def query_pokemon_by_types(types: list) -> list:
    """
    查询数据库中主属性或副属性包含指定属性之一的精灵。
    types: ["火系", "光系"]
    返回: 精灵详情字典列表（包含 stats）
    """
    if not types:
        return []

    # 构建 SQL 条件
    conditions = []
    for t in types:
        conditions.append(f"primary_type = '{t}'")
        conditions.append(f"secondary_type = '{t}'")
    where_clause = " OR ".join(conditions)

    sql = f"""
        SELECT p.*, ps.hp, ps.attack, ps.defense, ps.sp_attack, ps.sp_defense, ps.speed
        FROM pokemon p
        LEFT JOIN pokemon_stats ps ON p.id = ps.pokemon_id
        WHERE {where_clause}
        ORDER BY p.species_total DESC
    """
    try:
        results = default_executor.execute_query(sql)
        return results
    except Exception as e:
        print(f"[DB Tools] 查询精灵失败: {e}")
        return []