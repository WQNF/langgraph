from pymilvus import connections, Collection, utility

connections.connect(host="localhost", port="19530")
print("集合列表：", utility.list_collections())

col = Collection("knowledge_base")
col.load()

print("实体总数：", col.num_entities)
print("Schema字段：", [f.name for f in col.schema.fields])

# 直接执行您用的查询
expr = 'text like "%【火系】%"'
print("执行查询：", expr)
try:
    res = col.query(expr=expr, output_fields=["text"], limit=2)
    print("查询结果数量：", len(res))
    if res:
        print("第一条的text字段内容：", res[0].get("text", "无text字段！")[:100])
    else:
        print("结果为空。尝试输出所有可用字段名：")
        if col.schema:
            print([f.name for f in col.schema.fields])
except Exception as e:
    print("查询出错：", e)