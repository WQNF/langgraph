# agents/team_analyzer.py
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer
from core.llm import llm
from tools.rag_tools import retrieve_attribute_docs
from tools.db_tools import query_pokemon_by_types
from tools.team_utils import extract_weaknesses_from_analysis

VALID_ELEMENTS = [
    "火系", "水系", "草系", "光系", "恶系", "幽系",
    "普通系", "地系", "冰系", "龙系", "电系", "毒系",
    "虫系", "武系", "翼系", "萌系", "机械系", "幻系"
]

def _format_team_data(pokemons: list) -> str:
    lines = []
    for poke in pokemons:
        name = poke["name"]
        primary = poke["primary_type"]
        secondary = poke.get("secondary_type")
        types = f"{primary}" + (f" + {secondary}" if secondary else "")
        total = poke.get("species_total", "?")
        ability = poke.get("ability", "无")
        stats = poke.get("stats", {})
        hp = stats.get("hp", "?")
        atk = stats.get("attack", "?")
        spa = stats.get("sp_attack", "?")
        def_ = stats.get("defense", "?")
        spd = stats.get("sp_defense", "?")
        spe = stats.get("speed", "?")
        line = (
            f"{name} (属性: {types}, 特性: {ability}, 种族值和: {total}, "
            f"HP:{hp} 物攻:{atk} 魔攻:{spa} 物防:{def_} 魔防:{spd} 速度:{spe})"
        )
        lines.append(line)
    return "\n".join(lines)

def team_analyzer(state: dict) -> dict:
    writer = get_stream_writer()
    preloaded_team = state.get("preloaded_team", [])
    user_input = state.get("user_input", "")
    
    print(f"\n【team_analyzer】开始分析队伍，共{len(preloaded_team)}只精灵")
    elements_list = ", ".join(VALID_ELEMENTS)

    # ── Step 1: 获取属性克制信息（优先使用精灵自带的attribute_relations） ──
    writer({"type": "info", "content": "🔍 正在获取属性克制信息..."})
    all_attr_docs = []
    for poke in preloaded_team:
        if poke.get('attribute_relations'):
            all_attr_docs.append(poke['attribute_relations'])
            print(f"  【{poke['name']}】使用内置属性关系")
            print(poke['attribute_relations'])
        else:
            primary = poke.get("primary_type")
            secondary = poke.get("secondary_type")
            attrs = []
            if secondary:
                attrs = [f"{primary}+{secondary}", f"{secondary}+{primary}"]
            elif primary:
                attrs = [primary]
            if attrs:
                docs = retrieve_attribute_docs(attrs, user_query=user_input)
                all_attr_docs.extend(docs)
                print(f"  【{poke['name']}】从向量数据库检索到{len(docs)}个文档")

    # ── Step 2: 第一次分析队伍优劣势 ──
    writer({"type": "info", "content": "📊 正在分析队伍优劣势..."})
    context_1 = "\n\n".join(all_attr_docs)
    team_text = _format_team_data(preloaded_team)
    prompt_1 = f"""你是队伍分析专家。你必须严格遵守【最重要规则】内容，生成最终答案，请基于以下属性克制文档和队伍数据，分析这个队伍的打击面、联防弱点、抵抗面。
【最重要规则】
1、本游戏只有以下18种属性{elements_list}以及这18种属行中的任意两个属性的组合，
2、禁止提及或编造任何其他属性名称（如"钢系""超能系""妖精系"等都不存在），不要添加和减少字，例如：“恶系”就是“恶系”不要变成恶魔系。
3、名词解释：①（强力克制）指一种属性技能可以克制某两种属性组和，造成3倍伤害；②（强力抵抗）指某只双属性精灵的两个属性抵抗敌方精灵释放的某一个属性技能，只受到1/3的伤害。
4、队伍数据中的属性克制关系是准确的克制关系，里面有单属性克制关系，和双属性克制关系。

{context_1}
【队伍数据】
{team_text}

请用中文输出分析报告，包含：1. 打击面覆盖 2. 联防弱点 3. 抵抗面 4. 整体评价。"""

    first_analysis = ""
    for chunk in llm.stream(prompt_1):
        token = chunk.content
        if token:
            first_analysis += token
            writer({"type": "token", "content": token})
    writer({"type": "info", "content": "\n"})

    # ── Step 3: 判断队伍是否已满 ──
    if len(preloaded_team) >= 6:
        print(f"\n【team_analyzer】队伍已满({len(preloaded_team)}只)，跳过推荐精灵步骤")
        final_answer = first_analysis
    else:
        # ── Step 4: 提取弱点，查找适配精灵 ──
        writer({"type": "info", "content": "🔎 正在搜索适配的精灵..."})
        weaknesses = extract_weaknesses_from_analysis(first_analysis)
        print(f"\n【team_analyzer】提取到的弱点属性: {weaknesses}")
        
        if not weaknesses:
            print("  未检测到弱点，不进行精灵推荐")
            final_answer = first_analysis + "\n（未检测到明显弱点，无法给出补充建议）"
        else:
            target_types = weaknesses[:2]
            print(f"\n【team_analyzer】基于弱点 {target_types} 搜索推荐精灵")
            recommend_pokemons = query_pokemon_by_types(target_types)
            print(f"  查询到 {len(recommend_pokemons)} 只推荐精灵")

            if not recommend_pokemons:
                final_answer = first_analysis + f"\n（数据库中没有找到能弥补弱点（{', '.join(target_types)}）的精灵，请手动调整队伍）"
            else:
                recommend_pokemons = recommend_pokemons[:5]
                print(f"  取前 {len(recommend_pokemons)} 只精灵进行推荐分析")

                # 只有在需要推荐精灵时才检索向量数据库
                writer({"type": "info", "content": "🔎 正在检索推荐精灵的克制信息..."})
                recommend_docs = []
                for rp in recommend_pokemons:
                    primary = rp.get("primary_type")
                    secondary = rp.get("secondary_type")
                    attrs = []
                    if secondary:
                        attrs = [f"{primary}+{secondary}", f"{secondary}+{primary}"]
                    elif primary:
                        attrs = [primary]
                    if attrs:
                        docs = retrieve_attribute_docs(attrs, user_query=user_input)
                        recommend_docs.extend(docs)
                        print(f"  【{rp['name']}】检索到{len(docs)}个文档")

                context_2 = "\n\n".join(all_attr_docs + recommend_docs)
                recommend_text = _format_team_data(recommend_pokemons)

                # ── Step 5: 第二次分析 ──
                writer({"type": "info", "content": "📝 正在生成搭配建议..."})
                prompt_2 = f"""你是队伍构建大师。基于以下属性克制文档、原始队伍分析、以及从数据库中查询到的**真实可用的精灵**，给出最终队伍优化建议。
【属性克制文档】
{context_2}
【原始队伍分析】
{first_analysis}
【数据库中的可选精灵（只能从其中选择推荐）】
{recommend_text}
【重要】本游戏只有以下18种属性，禁止提及或编造任何其他属性名称：
{elements_list}
要求：
1. 必须从上述【数据库中的可选精灵】中选择精灵进行推荐，绝对禁止推荐任何未列出的精灵。
2. 分析加入后对队伍的提升，以及可能的负面影响。
3. 如果某个精灵不适合（属性冲突、种族值太低等），请说明理由并排除。
请输出：1. 推荐替换的精灵及理由 2. 加入后的效果 3. 最终优化后的阵容（列出具体精灵名称）。"""

                final_answer = ""
                for chunk in llm.stream(prompt_2):
                    token = chunk.content
                    if token:
                        final_answer += token
                        writer({"type": "token", "content": token})

    print(f"\n【team_analyzer】最终返回信息:")
    print(f"  - 最终答案长度: {len(final_answer)} 字符")
    print(f"  - 任务完成状态: True")
    print(f"  - 步骤计数: {state.get('step_count', 0) + 1}")
    print(f"  - 预加载队伍精灵数: {len(preloaded_team)}")
    
    return {
        "messages": [AIMessage(content=final_answer)],
        "task_completed": True,
        "step_count": state.get("step_count", 0) + 1,
        "compressed_context": state.get("compressed_context", ""),
        "preloaded_pokemons": state.get("preloaded_pokemons", []),
        "preloaded_elements": state.get("preloaded_elements", []),
        "preloaded_team": preloaded_team,
    }