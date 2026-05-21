# Skills 说明书

## 1. 精灵查询技能 (pokemon_lookup)

### 描述
查询精灵基础信息，包括种族值、属性、特性等。

### 使用的工具/Agent
- 数据库查询工具（pokemon_agent）

### 专属 System Prompt
"你是精灵图鉴助手，请根据数据库准确回答精灵信息。"

### 参数
- `pokemon_name` (str): 精灵名称
- `info_types` (list, optional): 需要查询的信息类型，如['type', 'stats', 'ability']

### 返回值
- `success` (bool): 操作是否成功
- `data` (dict): 精灵的详细信息
  - `name` (str): 精灵名称
  - `types` (list): 属性类型列表
  - `stats` (dict): 种族值信息
  - `abilities` (list): 特性列表
- `metadata` (dict): 元数据信息
- `error` (str, optional): 错误信息（当success为False时）

### 要点
- 从数据库准确获取精灵基础信息
- 提供完整的种族值、属性、特性等数据
- 支持按需查询特定信息类型

---

## 2. 属性分析技能 (type_analysis)

### 描述
进行单/双属性克制关系分析，基于属性克制表文档进行分析。

### 使用的工具/Agent
- 向量检索工具（rag_agent）+ 数据库查询（获取属性）

### 专属 System Prompt
"你是属性对战分析师，严格基于属性克制表文档分析克制/被克/抵抗关系，禁止编造。"

### 参数
- `attacking_type` (str or list): 攻击方属性（可单属性或双属性）
- `defending_type` (str or list): 防御方属性（可单属性或双属性）
- `analysis_type` (str, optional): 分析类型（'offensive'进攻方分析, 'defensive'防御方分析）

### 返回值
- `success` (bool): 操作是否成功
- `data` (dict): 分析结果
  - `multiplier` (float): 伤害倍率
  - `relationship` (str): 克制关系描述
  - `details` (dict): 详细分析过程
- `metadata` (dict): 元数据信息
- `error` (str, optional): 错误信息（当success为False时）

### 要点
- 严格基于属性克制表文档进行分析
- 禁止编造未在文档中提及的信息
- 支持单属性和双属性分析
- 提供详细的克制关系说明

---

## 3. 队伍协同分析技能 (team_synergy)

### 描述
进行队伍联防与打击面分析，适用于多只精灵组成的队伍。

### 使用的工具/Agent
- 数据库查询（获取各精灵属性）+ 向量检索（获取克制表）+ LLM 综合分析

### 专属 System Prompt
"你是顶级队伍构建师，请基于全队属性分析联防盲点、致命弱点、打击面覆盖，并给出配队建议。"

### 参数
- `team_list` (list): 精灵名称列表
- `analysis_depth` (str, optional): 分析深度（'basic', 'advanced'）

### 返回值
- `success` (bool): 操作是否成功
- `data` (dict): 分析结果
  - `synergy_score` (float): 协同评分
  - `coverage` (dict): 打击面分析
  - `weaknesses` (list): 联防盲点和弱点
  - `recommendations` (list): 配队建议
- `metadata` (dict): 元数据信息
- `error` (str, optional): 错误信息（当success为False时）

### 要点
- 分析队伍的整体联防能力
- 识别队伍的盲点和致命弱点
- 评估打击面覆盖范围
- 提供具体的配队改进建议

---