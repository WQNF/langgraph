# test_ability.py
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_pokemon_ability(pokemon_id: int = 1):
    """测试指定精灵 ID 的详情接口，检查 ability 字段"""
    url = f"{BASE_URL}/pokemon/{pokemon_id}"
    try:
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ 成功获取精灵 ID {pokemon_id} 的数据")
            print(f"   名称: {data.get('name', '无')}")
            ability = data.get('ability', 'MISSING')
            print(f"   特性(ability): {ability}")
            if ability == 'MISSING':
                print("   ⚠️ ability 字段缺失！请检查后端数据模型或序列化配置")
            else:
                print("   ability 字段正常")
        else:
            print(f"❌ 请求失败，状态码: {resp.status_code}")
            print(f"   响应内容: {resp.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    # 可修改 ID 列表，逐一检测
    test_ids = [10, 22, 3]  # 根据你的数据库实际 ID 调整
    for pid in test_ids:
        test_pokemon_ability(pid)
        print("-" * 40)