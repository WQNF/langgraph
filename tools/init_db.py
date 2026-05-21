import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "omnipilot",
    "password": "omnipilot123",
    "database": "omnipilot"
}

SQL_CREATE_TABLES = """
-- 彻底清除旧表（避免重复数据）
DROP TABLE IF EXISTS pokemon_stats CASCADE;
DROP TABLE IF EXISTS pokemon CASCADE;

-- 启用模糊搜索扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 精灵基本信息表
CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    national_number VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    primary_type VARCHAR(10) NOT NULL,
    secondary_type VARCHAR(10),
    species_total INTEGER NOT NULL,
    ability TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 种族值详情表
CREATE TABLE pokemon_stats (
    id SERIAL PRIMARY KEY,
    pokemon_id INTEGER NOT NULL UNIQUE REFERENCES pokemon(id) ON DELETE CASCADE,
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    sp_attack INTEGER NOT NULL,
    sp_defense INTEGER NOT NULL,
    speed INTEGER NOT NULL
);

-- 查询加速索引
CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon(name);
CREATE INDEX IF NOT EXISTS idx_pokemon_primary_type ON pokemon(primary_type);
CREATE INDEX IF NOT EXISTS idx_pokemon_name_trgm ON pokemon USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_pokemon_ability_trgm ON pokemon USING gin (ability gin_trgm_ops);
"""

SQL_INSERT_POKEMON = """
INSERT INTO pokemon (national_number, name, primary_type, secondary_type, species_total, ability) VALUES
('001', '迪莫', '光系', NULL, 582, '最好的伙伴：造成克制伤害后，获得攻防速+20%，并回复2能量。'),
('002', '喵喵', '草系', NULL, 346, '氧循环：释放草系技能时，回复10%最大生命值。'),
('003', '喵呜', '草系', NULL, 437, '氧循环：使用草系技能后，回复10%最大生命值。'),
('004', '魔力猫', '草系', NULL, 546, '氧循环：使用草系技能后，回复10%最大生命值。'),
('005', '火花', '火系', NULL, 382, '助燃：释放火系技能后，攻击提升20%。'),
('006', '焰火', '火系', NULL, 490, '助燃：释放火系技能后，攻击提升20%。'),
('007', '火神', '火系', NULL, 613, '助燃：释放火系技能后，攻击提升20%。'),
('008', '水蓝蓝', '水系', NULL, 361, '浸润：释放水系技能时，所有技能能耗-1。'),
('009', '波波拉', '水系', NULL, 497, '浸润：释放水系技能时，所有技能能耗-1。'),
('010', '水灵', '水系', NULL, 621, '浸润：释放水系技能时，所有技能能耗-1。'),
('011', '鸭吉吉', '普通系', NULL, 471, '蓬松的样子：携带的能耗为1的技能，威力+50%。'),
('012', '板板壳', '水系', NULL, 357, '缩壳：携带的防御技能能耗-2。'),
('013', '咔咔壳', '水系', NULL, 475, '缩壳：携带的防御技能能耗-2。'),
('014', '水泡壳', '水系', NULL, 594, '缩壳：携带的防御技能能耗-2。'),
('015', '锥尾羊', '幽系', NULL, 349, '碰瓷：自己使用恶系技能后，敌方失去2能量。'),
('016', '铃兰羊', '幽系', NULL, 466, '碰瓷：自己使用恶系技能后，敌方失去2能量。'),
('017', '花影羚羊', '幽系', '恶系', 582, '碰瓷：自己使用恶系技能后，敌方失去2能量。'),
('018', '雪绒鸟', '翼系', NULL, 335, '顺风：若先于敌方攻击，本次技能威力+50%。'),
('019', '冬羽雀', '翼系', NULL, 456, '顺风：若先于敌方攻击，本次技能威力+50%。'),
('020', '岚鸟', '翼系', NULL, 570, '顺风：若先于敌方攻击，本次技能威力+50%。'),
('021', '小灵菇', '幽系', NULL, 374, '毒蘑菇：回合结束时，偷取敌方场上所有精灵1能量。'),
('022', '幻灵菇', '幽系', '草系', 499, '毒蘑菇：回合结束时，偷取敌方场上所有精灵1能量。'),
('023', '幻影灵菇', '幽系', '草系', 621, '毒蘑菇：回合结束时，偷取敌方场上所有精灵1能量。'),
('024', '石肤蜥', '地系', NULL, 343, '刺肤：每受到1次攻击，对攻击自己的精灵造成50威力的物理伤害。'),
('025', '石刺蜥', '地系', NULL, 458, '刺肤：每受到1次攻击，对攻击自己的精灵造成50威力的物理伤害。'),
('026', '石冠王蜥', '地系', NULL, 572, '刺肤：每受到1次攻击，对攻击自己的精灵造成50威力的物理伤害。'),
('027', '布是石', '地系', NULL, 409, '地脉：初始能量为0，入场前己方精灵每放一次地系技能，回复3能量。'),
('028', '布是岩', '地系', NULL, 546, '地脉：初始能量为0，入场前己方精灵每放一次地系技能，回复3能量。'),
('029', '布克棱岩', '地系', NULL, 683, '地脉：初始能量为0，入场前己方精灵每放一次地系技能，回复3能量。'),
('030', '恶魔叮', '恶系', '翼系', 427, '渴求：入场时获得50%吸血。'),
('031', '叮叮恶魔', '恶系', '翼系', 535, '渴求：入场时获得50%吸血。'),
('032', '毛毛', '虫系', '萌系', 228, '化茧：受到致命伤害时，获得一层萌化，并免疫此次伤害。'),
('033', '爬爬', '虫系', '萌系', 302, '化茧：受到致命伤害时，获得一层萌化，并免疫此次伤害。'),
('034', '化蝶', '虫系', '萌系', 377, '化茧：受到致命伤害时，获得一层萌化，并免疫此次伤害。'),
('035', '幽影树', '草系', '幽系', 571, '小偷小摸：入场时偷取敌方所有精灵2能量。'),
('036', '小鼠獭', '普通系', '水系', 355, '保守派：总能耗小于4时，自己获得双防+80%。'),
('037', '燕尾獭', '普通系', '水系', 477, '保守派：总能耗小于4时，自己获得双防+80%。'),
('038', '卷胡巨獭', '普通系', '水系', 595, '保守派：总能耗小于4时，自己获得双防+80%。'),
('039', '矿晶虫', '光系', '地系', 466, '偏振：受到自己携带技能系别的攻击伤害-40%。'),
('040', '晶石蜗', '光系', '地系', 583, '偏振：受到自己携带技能系别的攻击伤害-40%。'),
('041', '奇丽草', '草系', NULL, 383, '养分重吸收：回合结束时，回复3能量。'),
('042', '奇丽叶', '草系', NULL, 511, '养分重吸收：回合结束时，回复3能量。'),
('043', '奇丽花', '草系', NULL, 638, '养分重吸收：回合结束时，回复3能量。'),
('044', '丢丢', '草系', NULL, 268, '诈死：自己力竭时，少损失1点魔力。'),
('045', '卡卡虫', '草系', NULL, 357, '诈死：自己力竭时，少损失1点魔力。'),
('046', '卡瓦重', '草系', NULL, 447, '诈死：自己力竭时，少损失1点魔力。'),
('047', '护主犬', '火系', NULL, 451, '专注力：入场首回合，获得物攻+100%。'),
('048', '音速犬', '火系', NULL, 562, '专注力：入场首回合，获得物攻+100%。'),
('049', '绿耳松鼠', '普通系', NULL, 333, '囤积：每有1能量，获得双防+10%。'),
('050', '抱枕松鼠', '普通系', NULL, 445, '囤积：每有1能量，获得双防+10%。'),
('051', '蹦床松鼠', '普通系', NULL, 555, '囤积：每有1能量，获得双防+10%。'),
('052', '嘟嘟煲', '毒系', NULL, 459, '复方汤剂：回合结束时，中毒效果触发次数+1。'),
('053', '嘟嘟锅', '毒系', NULL, 573, '复方汤剂：回合结束时，中毒效果触发次数+1。'),
('054', '小灵面', '幽系', NULL, 366, '惊吓：能量等于0的精灵，无法对自己造成伤害。'),
('055', '暗影灵面', '幽系', NULL, 488, '惊吓：能量等于0的精灵，无法对自己造成伤害。'),
('056', '幽冥眼', '幽系', NULL, 610, '惊吓：能量等于0的精灵，无法对自己造成伤害。'),
('057', '梦游', '幽系', NULL, 462, '做噩梦：敌方精灵离场后，更换入场的精灵失去3能量。'),
('058', '梦悠悠', '幽系', NULL, 579, '做噩梦：敌方精灵离场后，更换入场的精灵失去3能量。'),
('059', '兽花蕾', '光系', '草系', 513, '稀兽花宝：根据自己的血脉，入场时获得不同的效果。'),
('060', '伏地兽', '普通系', NULL, 338, '壮胆：队伍存在虫系精灵，自己获得双攻+50%。'),
('061', '贪食鼹', '普通系', NULL, 449, '壮胆：队伍存在虫系精灵，自己获得双攻+50%。'),
('062', '巨噬针鼹', '普通系', NULL, 562, '壮胆：队伍存在虫系精灵，自己获得双攻+50%。'),
('063', '蹦蹦种子', '草系', '毒系', 348, '生物碱：使用草系技能时，敌方获得2层中毒。'),
('064', '蹦蹦草', '草系', '毒系', 464, '生物碱：使用草系技能时，敌方获得2层中毒。'),
('065', '蹦蹦花', '草系', '毒系', 580, '生物碱：使用草系技能时，敌方获得2层中毒。'),
('066', '电咩咩', '电系', NULL, 332, '快充：离场时回复10能量。'),
('067', '粉咩咩', '电系', NULL, 443, '快充：离场时回复10能量。'),
('068', '电球咩咩', '电系', NULL, 553, '快充：离场时回复10能量。'),
('069', '蒲公英', '草系', '萌系', 515, '勇敢：携带的能耗大于3的技能，威力+40%。'),
('070', '蒲公英娃娃', '草系', '萌系', 642, '勇敢：携带的能耗大于3的技能，威力+40%。'),
('071', '伊贝儿', '草系', NULL, 453, '腐植循环：每回复1能量，同时回复5%生命。'),
('072', '伊贝粉粉', '草系', NULL, 566, '腐植循环：每回复1能量，同时回复5%生命。'),
('073', '白发懒人', '普通系', NULL, 410, '慢热型：初始能量为0，队伍中其他精灵每应对成功一次回复5能量。'),
('074', '动力猿', '普通系', '武系', 547, '慢热型：初始能量为0，队伍中其他精灵每应对成功一次回复5能量。'),
('075', '瞌睡王', '普通系', '武系', 685, '慢热型：初始能量为0，队伍中其他精灵每应对成功一次回复5能量。'),
('076', '海盔虫', '水系', '毒系', 327, '溶解扩散：每携带1个毒系技能进入战斗，水系技能使敌方获得1层中毒。'),
('077', '刺盔虫', '水系', '毒系', 435, '溶解扩散：每携带1个毒系技能进入战斗，水系技能使敌方获得1层中毒。'),
('078', '千棘盔', '水系', '毒系', 545, '溶解扩散：每携带1个毒系技能进入战斗，水系技能使敌方获得1层中毒。'),
('079', '菊花梨', '萌系', NULL, 523, '无忧无虑：可获得的萌化层数不受限制。'),
('080', '小星光', '电系', NULL, 494, '电流刺激：携带的攻击技能获得迸发：威力+40。'),
('081', '星光狮', '电系', NULL, 617, '电流刺激：携带的攻击技能获得迸发：威力+40。'),
('082', '一窝蜂', '虫系', '翼系', 228, '虫群鼓舞：队伍中每有一只其他的虫系精灵，自己入场时获得攻防速+10%。'),
('083', '黄蜂后', '虫系', '翼系', 305, '虫群鼓舞：队伍中每有一只其他的虫系精灵，自己入场时获得攻防速+10%。'),
('084', '花魁蜂后', '虫系', '翼系', 382, '虫群鼓舞：队伍中每有一只其他的虫系精灵，自己入场时获得攻防速+10%。'),
('085', '小夜', '恶系', NULL, 374, '嫁祸：自己每失去25%生命，连击数+2。'),
('086', '紫夜', '恶系', NULL, 499, '嫁祸：自己每失去25%生命，连击数+2。'),
('087', '朔夜伊芙', '恶系', NULL, 624, '嫁祸：自己每失去25%生命，连击数+2。'),
('088', '乖乖鹄', '翼系', '水系', 394, '洁癖：离场后，自己的增益和减益会被更换入场的精灵继承。'),
('089', '蓝珠天鹅', '翼系', '水系', 525, '洁癖：离场后，自己的增益和减益会被更换入场的精灵继承。'),
('090', '翠顶夫人', '翼系', '水系', 656, '洁癖：离场后，自己的增益和减益会被更换入场的精灵继承。'),
('091', '黑羽夫人', '翼系', '恶系', 652, '孤傲：敌方精灵离场后，其增益和减益会被更换入场的精灵继承。'),
('092', '锤头鹳', '翼系', '水系', 511, '块锤：携带的能耗小于3的技能，获得迅捷。'),
('093', '绿草精灵', '草系', '幻系', 473, '木桶戏法：离场后，更换入场的精灵以木桶状态登场。'),
('094', '魔草巫灵', '草系', '幻系', 592, '木桶戏法：离场后，更换入场的精灵以木桶状态登场。'),
('095', '记忆石', '地系', NULL, 607, '不移：携带的无额外效果的攻击技能，威力+30%。'),
('096', '咔咔羽毛', '翼系', '普通系', 378, '卡卡冲刺：若先于敌方行动，行动后获得连击数+1。'),
('097', '咔咔雀', '翼系', '普通系', 505, '卡卡冲刺：若先于敌方行动，行动后获得连击数+1。'),
('098', '咔咔鸟', '翼系', '普通系', 631, '卡卡冲刺：若先于敌方行动，行动后获得连击数+1。'),
('099', '小草虫', '虫系', '草系', 323, '花精灵：回合结束时，己方队伍获得1次随机奉献。'),
('100', '草衣虫', '草系', '虫系', 429, '花精灵：回合结束时，己方队伍获得1次随机奉献。'),
('101', '花衣蝶', '草系', '虫系', 539, '花精灵：回合结束时，己方队伍获得1次随机奉献。'),
('102', '绿翼鸟', '萌系', '翼系', 330, '自由飘：自己每有一层萌化，获得连击数+2。'),
('103', '魔翼鸟', '萌系', '翼系', 441, '自由飘：自己每有一层萌化，获得连击数+2。'),
('104', '魔眷鸟', '萌系', '翼系', 551, '自由飘：自己每有一层萌化，获得连击数+2。'),
('105', '阿米亚特', '地系', NULL, 360, '石头大餐：能量不足时，消耗5%生命，代替1能量。'),
('106', '阿米樱', '地系', NULL, 480, '石头大餐：能量不足时，消耗5%生命，代替1能量。'),
('107', '罗隐', '地系', '恶系', 601, '石头大餐：能量不足时，消耗5%生命，代替1能量。'),
('108', '风铃鲨', '水系', '翼系', 347, '水翼推进：己方精灵每使用一次水系技能，自己入场时获得全技能能耗-1。'),
('109', '蓝蝶鲨', '水系', '翼系', 462, '水翼推进：己方精灵每使用一次水系技能，自己入场时获得全技能能耗-1。'),
('110', '彩蝶鲨', '水系', '翼系', 579, '水翼推进：己方精灵每使用一次水系技能，自己入场时获得全技能能耗-1。'),
('111', '石石', '地系', NULL, 467, '石天平：若使用技能能耗高于敌方，回合结束使敌方失去能耗之差的能量。'),
('112', '巨灵石', '地系', '幽系', 584, '石天平：若使用技能能耗高于敌方，回合结束使敌方失去能耗之差的能量。'),
('113', '仪使者', '地系', '幻系', 366, '观星：敌方每有一层星陨印记，自己的地系技能威力+15%。'),
('114', '仪式之星', '地系', '幻系', 488, '观星：敌方每有一层星陨印记，自己的地系技能威力+15%。'),
('115', '仪式巨象', '地系', '幻系', 610, '观星：敌方每有一层星陨印记，自己的地系技能威力+15%。'),
('116', '小独角兽', '光系', NULL, 476, '目空：携带的非光系技能，威力+25%。'),
('117', '白金独角兽', '光系', NULL, 595, '目空：携带的非光系技能，威力+25%。'),
('118', '旋叶虫', '普通系', '虫系', 326, '共鸣：携带的【虫鸣】技能威力+20。'),
('119', '蓬叶虫', '普通系', '虫系', 433, '共鸣：携带的【虫鸣】技能威力+20。'),
('120', '风滚暮虫', '普通系', '虫系', 542, '共鸣：携带的【虫鸣】技能威力+20。'),
('121', '小黑猫', '普通系', NULL, 528, '预警：若敌方技能足够击败自己，回合开始时自己获得速度+50。'),
('122', '黑猫巫师', '普通系', NULL, 662, '预警：若敌方技能足够击败自己，回合开始时自己获得速度+50。'),
('123', '忽幽狸', '幽系', '毒系', 493, '下黑手：敌方精灵离场后，更换入场的精灵获得5层中毒。'),
('124', '影狸', '幽系', '毒系', 616, '下黑手：敌方精灵离场后，更换入场的精灵获得5层中毒。'),
('125', '多多', '毒系', '地系', 355, '毒牙：使敌方获得中毒时，也会使其获得魔攻和魔防-40%。'),
('126', '多啦多', '毒系', '地系', 472, '毒牙：使敌方获得中毒时，也会使其获得魔攻和魔防-40%。'),
('127', '古啦多', '毒系', '地系', 591, '毒牙：使敌方获得中毒时，也会使其获得魔攻和魔防-40%。'),
('128', '哭哭菇', '幻系', NULL, 279, '吸积盘：回合结束时，敌方获得2层星陨印记。'),
('129', '怖须菇', '幻系', NULL, 372, '吸积盘：回合结束时，敌方获得2层星陨印记。'),
('130', '怖哭菇', '幻系', NULL, 466, '吸积盘：回合结束时，敌方获得2层星陨印记。'),
('131', '恶魔狼', '恶系', NULL, 548, '悲悯：己方队伍中每有1只力竭的精灵，自己获得双攻+30%。'),
('132', '小电企鹅', '冰系', '电系', 467, '超负荷：攻击技能获得迸发+敌方获得全技能能耗+1。'),
('133', '电企鹅', '冰系', '电系', 583, '超负荷：攻击技能获得迸发+敌方获得全技能能耗+1。'),
('134', '雪豆丁', '冰系', NULL, 429, '打雪仗：初始能量为0，入场前己方精灵每放1次冰系技能，回复3能量。'),
('135', '雪蛮人', '冰系', NULL, 574, '打雪仗：初始能量为0，入场前己方精灵每放1次冰系技能，回复3能量。'),
('136', '雪巨人', '冰系', NULL, 718, '打雪仗：初始能量为0，入场前己方精灵每放1次冰系技能，回复3能量。'),
('137', '呼呼猪', '冰系', '地系', 463, '冻土：每携带1个冰系技能进入战斗，地系技能威力+10%。'),
('138', '獠牙猪', '冰系', '地系', 579, '冻土：每携带1个冰系技能进入战斗，地系技能威力+10%。'),
('139', '雪娃娃', '冰系', NULL, 385, '冰封：在场时，敌方全技能能耗+1。'),
('140', '冰封怨灵', '冰系', NULL, 515, '冰封：在场时，敌方全技能能耗+1。'),
('141', '雪灵', '冰系', NULL, 643, '冰封：在场时，敌方全技能能耗+1。'),
('142', '大耳帽兜', '冰系', '萌系', 370, '捉迷藏：使敌方获得冻结时，也会使其获得全技能能耗+1。'),
('143', '帽兜娃娃', '冰系', '萌系', 493, '捉迷藏：使敌方获得冻结时，也会使其获得全技能能耗+1。'),
('144', '雪影娃娃', '冰系', '萌系', 617, '捉迷藏：使敌方获得冻结时，也会使其获得全技能能耗+1。'),
('145', '权杖-Ⅱ', '机械系', NULL, 522, '机械变式：自己携带的技能每回合位置变化时，该技能能耗-1。'),
('146', '权杖-Ⅴ', '机械系', NULL, 652, '机械变式：自己携带的技能每回合位置变化时，该技能能耗-1。'),
('147', '灵狐', '火系', '冰系', 347, '灵魂灼伤：冰系技能使敌方获得4层灼烧，火系技能使敌方获得2层冻结。'),
('148', '九尾狐', '火系', '冰系', 465, '灵魂灼伤：冰系技能使敌方获得4层灼烧，火系技能使敌方获得2层冻结。'),
('149', '尖嘴狐仙', '火系', '冰系', 580, '灵魂灼伤：冰系技能使敌方获得4层灼烧，火系技能使敌方获得2层冻结。'),
('150', '里奥', '翼系', NULL, 411, '飓风：对本精灵的技能，若其他翼系精灵携带相同的技能，则获得迅捷。被敌方精灵击败时，自己额外损失1点魔力。'),
('151', '灵羽勇士', '翼系', NULL, 547, '飓风：对本精灵的技能，若其他翼系精灵携带相同的技能，则获得迅捷。被敌方精灵击败时，自己额外损失1点魔力。'),
('152', '圣羽翼王', '翼系', NULL, 686, '飓风：对本精灵的技能，若其他翼系精灵携带相同的技能，则获得迅捷。被敌方精灵击败时，自己额外损失1点魔力。'),
('153', '松仔', '草系', '武系', 380, '野性感官：应对成功后，下次行动先手+1。'),
('154', '松叶羊', '草系', '武系', 507, '野性感官：应对成功后，下次行动先手+1。'),
('155', '针叶巡林', '草系', '武系', 634, '野性感官：应对成功后，下次行动先手+1。'),
('156', '小勇狮', '火系', '武系', 358, '圣火骑士：应对成功后，下次攻击威力翻倍。'),
('157', '炽焰狮', '火系', '武系', 478, '圣火骑士：应对成功后，下次攻击威力翻倍。'),
('158', '炽心勇狮', '火系', '武系', 597, '圣火骑士：应对成功后，下次攻击威力翻倍。'),
('159', '水滴蛇', '水系', '武系', 378, '思维之盾：应对成功后，下次行动技能能耗-5。'),
('160', '水蛇锁', '水系', '武系', 505, '思维之盾：应对成功后，下次行动技能能耗-5。'),
('161', '游蛇魔使', '水系', '武系', 630, '思维之盾：应对成功后，下次行动技能能耗-5。'),
('162', '公平鸽', '普通系', NULL, 649, '衡量：入场时，复制敌方的增益。在场时若敌方获得增益自己也会获得。'),
('163', '小怂猫', '武系', NULL, 522, '威慑：打断敌方时，被打断的技能进入2回合冷却。'),
('164', '怒目怂猫', '武系', NULL, 651, '威慑：打断敌方时，被打断的技能进入2回合冷却。'),
('165', '小狮鹫', '翼系', NULL, 338, '乘风连击：使用翼系技能后，获得连击数+1。'),
('166', '神圣狮鹫', '翼系', NULL, 451, '乘风连击：使用翼系技能后，获得连击数+1。'),
('167', '皇家狮鹫', '翼系', NULL, 564, '乘风连击：使用翼系技能后，获得连击数+1。'),
('168', '圆眼蜘蛛', '虫系', NULL, 305, '毒腺：使用能耗小于等于1的技能时，敌方获得4层中毒。'),
('169', '尖角蜘蛛', '虫系', NULL, 406, '毒腺：使用能耗小于等于1的技能时，敌方获得4层中毒。'),
('170', '芋香巨角蛛', '虫系', '毒系', 506, '毒腺：使用能耗小于等于1的技能时，敌方获得4层中毒。'),
('171', '波波螺', '地系', '水系', 380, '消波块：每携带1个水系技能进入战斗，地系技能能耗-1。'),
('172', '消波螺', '地系', '水系', 505, '消波块：每携带1个水系技能进入战斗，地系技能能耗-1。'),
('173', '嗜波螺', '地系', '水系', 634, '消波块：每携带1个水系技能进入战斗，地系技能能耗-1。'),
('174', '菇菇丁', '地系', '草系', 376, '多人宿舍：自己的能量可以超过能量上限。'),
('175', '多菇丁', '地系', '草系', 501, '多人宿舍：自己的能量可以超过能量上限。'),
('176', '九幽菇', '地系', '草系', 627, '多人宿舍：自己的能量可以超过能量上限。'),
('177', '斑斑', '翼系', NULL, 494, '逐魂鸟：能耗小于等于1的攻击技能，无法对自己造成伤害。'),
('178', '斑枭', '翼系', NULL, 617, '逐魂鸟：能耗小于等于1的攻击技能，无法对自己造成伤害。'),
('179', '草头鸭', '草系', NULL, 403, '得寸进尺：天气为雨天，或处在其他水系环境中时，获得双攻+100%。'),
('180', '卷毛鸭', '草系', '武系', 504, '得寸进尺：天气为雨天，或处在其他水系环境中时，获得双攻+100%。'),
('181', '海豹战士', '武系', '水系', 481, '身经百练：己方精灵每应对1次，自己入场时水系和武系技能威力+20%。'),
('182', '海豹船长', '水系', '武系', 600, '身经百练：己方精灵每应对1次，自己入场时水系和武系技能威力+20%。'),
('183', '号儿鱼', '水系', NULL, 460, '泛音列：使用状态技能后，敌方获得【聒噪】技能的效果，持续3回合。'),
('184', '圆号鱼', '水系', NULL, 575, '泛音列：使用状态技能后，敌方获得【聒噪】技能的效果，持续3回合。'),
('185', '甜田螺', '水系', '萌系', 370, '守护者：己方其他精灵每有一层萌化，自己入场时全技能能耗-1。'),
('186', '壳乙螺', '水系', '萌系', 495, '守护者：己方其他精灵每有一层萌化，自己入场时全技能能耗-1。'),
('187', '卡洛儿', '水系', '萌系', 619, '守护者：己方其他精灵每有一层萌化，自己入场时全技能能耗-1。'),
('188', '棋棋（白子）', '武系', '地系', 434, '腾挪：攻击技能应对1次后，回满状态，变为棋绮后。'),
('189', '棋骑士（白子）', '武系', '地系', 543, '腾挪：攻击技能应对1次后，回满状态，变为棋绮后。'),
('190', '棋齐垒（白子）', '武系', '地系', 489, '保卫：防御技能应对2次后，回满状态，变为棋绮后。'),
('191', '棋祈督（白子）', '武系', '地系', 547, '好象坏象：状态技能应对1次后，回满状态，变为棋绮后。'),
('192', '棋绮后（白子）', '武系', '地系', 508, '渗透：己方精灵每使用1次武系或地系技能，自己入场时获得攻防+5%。'),
('193', '奔波鼠', '地系', NULL, 451, '奔波命：使用防御技能后，回合结束时脱离。'),
('194', '流浪鼠', '地系', NULL, 563, '奔波命：使用防御技能后，回合结束时脱离。'),
('195', '呆小路', '草系', '萌系', 380, '营养液泡：获得增益时，额外获得层数+2。'),
('196', '舞动路路', '草系', '萌系', 507, '营养液泡：获得增益时，额外获得层数+2。'),
('197', '白发路路', '草系', '萌系', 633, '营养液泡：获得增益时，额外获得层数+2。'),
('198', '逗逗', '萌系', NULL, 384, '鼓气：使用能耗为3的技能时，获得攻防+20%。'),
('199', '气球猫', '萌系', NULL, 511, '鼓气：使用能耗为3的技能时，获得攻防+20%。'),
('200', '梦想三三', '萌系', NULL, 641, '鼓气：使用能耗为3的技能时，获得攻防+20%。'),
('201', '花怨鳗', '地系', '草系', 630, '铃兰晚钟：首次入场时，自己失去一半的当前生命值。'),
('202', '鳗尾兽', '地系', '草系', 788, '铃兰晚钟：首次入场时，自己失去一半的当前生命值。'),
('203', '伊雷龙', '龙系', NULL, 521, '嫉妒：蓄力状态下，可以使用任意携带技能。'),
('204', '伊兰亚龙', '龙系', NULL, 651, '嫉妒：蓄力状态下，可以使用任意携带技能。'),
('205', '拉特', '电系', NULL, 467, '噼啪！：入场后首次行动，所选技能使用次数+1。'),
('206', '酷拉', '电系', NULL, 583, '噼啪！：入场后首次行动，所选技能使用次数+1。'),
('207', '闪电环', '电系', NULL, 335, '防过载保护：每次行动后脱离。'),
('208', '刺电环', '电系', NULL, 446, '防过载保护：每次行动后脱离。'),
('209', '荆棘电环', '电系', NULL, 557, '防过载保护：每次行动后脱离。'),
('210', '小箱怪', '机械系', '幻系', 625, '虚假宝箱：自己力竭时，敌方获得攻防+20%。'),
('211', '迷迷箱怪', '机械系', '幻系', 782, '虚假宝箱：自己力竭时，敌方获得攻防+20%。'),
('212', '古钟蛇', '萌系', '毒系', 446, '拨浪鼓：己方精灵每使用一次状态技能，自己入场时毒系和萌系技能威力+10。'),
('213', '寒音蛇', '萌系', '毒系', 558, '拨浪鼓：己方精灵每使用一次状态技能，自己入场时毒系和萌系技能威力+10。'),
('214', '矮脚爬爬', '虫系', NULL, 532, '振奋虫心：主动击败敌方后，己方队伍获得5次随机奉献。'),
('215', '恶魔红钻', '虫系', '恶系', 666, '振奋虫心：主动击败敌方后，己方队伍获得5次随机奉献。'),
('216', '火尾瓦特', '火系', NULL, 338, '蒸汽膨胀：己方精灵每使用1次火系技能，自己入场时获得全技能威力+10。'),
('217', '火尾战士', '火系', NULL, 451, '蒸汽膨胀：己方精灵每使用1次火系技能，自己入场时获得全技能威力+10。'),
('218', '烈火守护', '火系', NULL, 564, '蒸汽膨胀：己方精灵每使用1次火系技能，自己入场时获得全技能威力+10。'),
('219', '里拉鳐', '水系', NULL, 644, '吟游之弦：赋予的印记不会替换其他印记，而是同时生效。'),
('220', '海枝枝', '水系', '幽系', 610, '珊瑚骨：敌方精灵离场时，自己获得全技能能耗-3。'),
('221', '多西', '机械系', '地系', 345, '定向精炼：己方精灵每使用1次防御技能，自己入场时机械系和地系技能威力+10%'),
('222', '库多西', '机械系', '地系', 459, '定向精炼：己方精灵每使用1次防御技能，自己入场时机械系和地系技能威力+10%'),
('223', '波多西', '机械系', '地系', 573, '定向精炼：己方精灵每使用1次防御技能，自己入场时机械系和地系技能威力+10%'),
('224', '小翼龙', '龙系', '翼系', 409, '暴食：携带的龙系技能获得迅捷。'),
('225', '翼龙', '龙系', '翼系', 513, '暴食：携带的龙系技能获得迅捷。'),
('226', '电动长颈鹿', '电系', NULL, 318, '蓄电池：每入场1次，永久获得双攻+20%。'),
('227', '奔乐鹿', '电系', NULL, 424, '蓄电池：每入场1次，永久获得双攻+20%。'),
('228', '爵士鹿', '电系', NULL, 532, '蓄电池：每入场1次，永久获得双攻+20%。'),
('229', '缇塔', '机械系', NULL, 454, '向心力：1号和2号位技能获得传动1和威力+30。'),
('230', '声波缇塔', '机械系', NULL, 568, '向心力：1号和2号位技能获得传动1和威力+30。'),
('231', '小鹬', '翼系', NULL, 320, '起飞加速：本场战斗首次使用的技能获得迅捷。'),
('232', '鄙目鹬', '翼系', NULL, 429, '起飞加速：本场战斗首次使用的技能获得迅捷。'),
('233', '高脚鹬', '翼系', NULL, 534, '起飞加速：本场战斗首次使用的技能获得迅捷。'),
('234', '脆筒甜甜', '冰系', NULL, 368, '加个雪球：使敌方获得冻结时，也会使其获得2层冻结。'),
('235', '香草甜甜', '冰系', NULL, 491, '加个雪球：使敌方获得冻结时，也会使其获得2层冻结。'),
('236', '圣代甜甜', '冰系', NULL, 611, '加个雪球：使敌方获得冻结时，也会使其获得2层冻结。'),
('237', '刺轮砣', '毒系', '萌系', 487, '耐活王：敌方受到中毒效果伤害使，自己回复等量生命。'),
('238', '月亮砣', '毒系', '萌系', 609, '耐活王：敌方受到中毒效果伤害使，自己回复等量生命。'),
('239', '豆丁鱼', '水系', '龙系', 401, '洄游：每次进入蓄力状态，获得全技能能耗永久-1。'),
('240', '快鳍鱼', '水系', '龙系', 534, '洄游：每次进入蓄力状态，获得全技能能耗永久-1。'),
('241', '龙鱼', '水系', '龙系', 667, '洄游：每次进入蓄力状态，获得全技能能耗永久-1。'),
('242', '胆小鳗鱼', '电系', '水系', 517, '生物电：携带的电系技能获得迸发：能耗-2。'),
('243', '闪电鳗鱼', '电系', '水系', 646, '生物电：携带的电系技能获得迸发：能耗-2。'),
('244', '翡翠水母', '水系', '毒系', 466, '扩散侵蚀：使用水系技能后，敌方获得中毒，获得层数等于中毒印记层数的2倍。'),
('245', '琉璃水母', '水系', '毒系', 580, '扩散溶解：使用水系技能后，敌方获得中毒，获得层数等于中毒印记层数的2倍。'),
('246', '裘洛', '毒系', NULL, 312, '蚀刻：回合结束时，敌方每2层中毒转化为1层中毒印记。'),
('247', '裘力', '毒系', NULL, 416, '蚀刻：回合结束时，敌方每2层中毒转化为1层中毒印记。'),
('248', '裘卡', '毒系', NULL, 520, '蚀刻：回合结束时，敌方每2层中毒转化为1层中毒印记。'),
('249', '可爱猿', '火系', NULL, 429, '散热：初始能量为0，入场前己方精灵每放一次火系技能，回复3能量。'),
('250', '炽热猿', '火系', NULL, 572, '散热：初始能量为0，入场前己方精灵每放一次火系技能，回复3能量。'),
('251', '火焰猿', '火系', NULL, 715, '散热：初始能量为0，入场前己方精灵每放一次火系技能，回复3能量。'),
('252', '布鲁斯', '冰系', NULL, 295, '冰钻：敌方携带技能总能耗每有1点，自己攻击时威力+10%。'),
('253', '雪顶布鲁斯', '冰系', NULL, 394, '冰钻：敌方携带技能总能耗每有1点，自己攻击时威力+10%。'),
('254', '冰钻布鲁斯', '冰系', NULL, 493, '冰钻：敌方携带技能总能耗每有1点，自己攻击时威力+10%。'),
('255', '治愈兔', '火系', '萌系', 358, '仁心：敌方受到灼烧伤害时，自己回复等量生命。'),
('256', '红丝绒', '火系', '萌系', 479, '仁心：敌方受到灼烧伤害时，自己回复等量生命。'),
('257', '红绒十字', '火系', '萌系', 598, '仁心：敌方受到灼烧伤害时，自己回复等量生命。'),
('258', '乌达（极昼）', '恶系', '火系', 369, '恶魔的晚宴：主动击败敌方精灵后，自己获得双攻+50%。'),
('259', '迷你乌（极昼）', '恶系', '火系', 492, '恶魔的晚宴：主动击败敌方精灵后，自己获得双攻+50%。'),
('260', '乌拉塔（极昼）', '恶系', '火系', 615, '恶魔的晚宴：主动击败敌方精灵后，自己获得双攻+50%。'),
('261', '螺旋帕帕', '机械系', '翼系', 377, '翼轴：1号位技能获得迅捷和传动1。'),
('262', '帕帕斯卡', '机械系', '翼系', 471, '翼轴：1号位技能获得迅捷和传动1。'),
('263', '机械方方', '机械系', NULL, 362, '盲拧：回合开始时，技能顺序打乱，四号位的技能能耗-4。'),
('264', '多彩方方', '机械系', NULL, 482, '盲拧：回合开始时，技能顺序打乱，四号位的技能能耗-4。'),
('265', '立方人', '机械系', NULL, 605, '盲拧：回合开始时，技能顺序打乱，四号位的技能能耗-4。'),
('266', '可立鸡', '火系', NULL, 396, '斗技：应对成功后，获得全技能威力永久+20。'),
('267', '晕晕鸡', '火系', NULL, 530, '斗技：应对成功后，获得全技能威力永久+20。'),
('268', '绅士鸡', '火系', '武系', 661, '指挥家：应对成功后，永久获得双攻+20%。'),
('269', '武者鸡', '火系', '武系', 580, '斗技：应对成功后，获得全技能威力永久+20。'),
('270', '优优', '地系', '光系', 485, '哨兵：回合开始时若敌方技能足够击败自己，自己获得速度+50，行动后脱离。'),
('271', '绒光优优', '地系', '光系', 605, '哨兵：回合开始时若敌方技能足够击败自己，自己获得速度+50，行动后脱离。'),
('272', '噼啪鸟', '电系', '翼系', 618, '连续负荷：自己技能的迸发效果延长1回合。'),
('273', '深蓝鲸', '水系', NULL, 588, '倾轧：携带的技能受能耗变化效果的影响翻倍。'),
('274', '格兰种子', '草系', NULL, 321, '生长：回合结束时，回复12%生命。'),
('275', '格兰花', '草系', NULL, 429, '生长：回合结束时，回复12%生命。'),
('276', '格兰球', '草系', NULL, 536, '生长：回合结束时，回复12%生命。'),
('277', '地鼠', '地系', NULL, 337, '警惕：回合结束时，若自己能量为0则脱离。'),
('278', '遁鼠', '地系', NULL, 450, '警惕：回合结束时，若自己能量为0则脱离。'),
('279', '遁地鼠', '地系', NULL, 562, '警惕：回合结束时，若自己能量为0则脱离。'),
('280', '墨鱿士', '幽系', NULL, 461, '涂鸦：使用非本系技能时威力+50%。'),
('281', '混乱鱿彩', '幽系', '恶系', 576, '涂鸦：使用非本系技能时威力+50%。'),
('282', '秩序鱿墨', '幽系', '萌系', 604, '绝对秩序：受到非敌方系别的技能攻击时伤害-50%。'),
('283', '小甲虫', '虫系', NULL, 418, '坚韧铠甲：每受到1次攻击伤害，己方队伍获得1次随机奉献。'),
('284', '铠甲虫', '虫系', NULL, 522, '坚韧铠甲：每受到1次攻击伤害，己方队伍获得1次随机奉献。'),
('285', '圣剑侍从', '机械系', NULL, 696, '正位宝剑：仅可使用1号位技能。'),
('286', '圣剑-X', '机械系', NULL, 868, '正位宝剑：仅可使用1号位技能。'),
('287', '吸泥鸥', '地系', '翼系', 455, '无差别过滤：在场时，所有精灵连击数固定为2。'),
('288', '泥吼牙', '地系', '翼系', 569, '无差别过滤：在场时，所有精灵连击数固定为2。'),
('289', '大骨头龙', '龙系', '幽系', 442, '不朽：力竭3回合后复活。'),
('290', '寂灭古龙', '龙系', '幽系', 552, '不朽：力竭3回合后复活。'),
('291', '厉毒小萝', '毒系', '恶系', 396, '侵蚀：敌方每有1层中毒效果，自己获得连击数+1。'),
('292', '厉毒修萝', '毒系', '恶系', 495, '侵蚀：敌方每有1层中毒效果，自己获得连击数+1。'),
('293', '小帕尔', '恶系', NULL, 379, '付给恶魔的代价：击败敌方精灵时，敌方额外损失1点魔力。被敌方精灵击败时，自己额外损失1点魔力。'),
('294', '帕尔萨斯', '恶系', NULL, 507, '付给恶魔的代价：击败敌方精灵时，敌方额外损失1点魔力。被敌方精灵击败时，自己额外损失1点魔力。'),
('295', '龙息帕尔', '恶系', NULL, 632, '付给恶魔的代价：击败敌方精灵时，敌方额外损失1点魔力。被敌方精灵击败时，自己额外损失1点魔力。'),
('296', '毛头小蛛', '虫系', '地系', 452, '扫拖一体：回合结束时驱散敌方1层印记，且驱散后己方队伍获得1次随机奉献。'),
('297', '捕尘长绒', '虫系', '地系', 565, '扫拖一体：回合结束时驱散敌方1层印记，且驱散后己方队伍获得1次随机奉献。'),
('298', '食尘短绒', '虫系', '地系', 576, '特殊清洁场景：回合结束时偷取敌方1层印记。'),
('299', '画精灵', '普通系', NULL, 371, '灰色肖像：攻击会使敌方已有的减益层数+3。'),
('300', '画像守护', '普通系', NULL, 494, '灰色肖像：攻击会使敌方已有的减益层数+3。'),
('301', '画间法师手', '普通系', NULL, 619, '灰色肖像：攻击会使敌方已有的减益层数+3。'),
('302', '画间沉铁兽', '普通系', '武系', 608, '变形活画：攻击时，敌方每有1层增益，本次技能威力+10%。'),
('303', '书魔虫', '普通系', NULL, 395, '图书守卫者：入场时，若自己的魔力值为1，自己获得双攻+50%。'),
('304', '书卷守护', '普通系', NULL, 527, '图书守卫者：入场时，若自己的魔力值为1，自己获得双攻+50%。'),
('305', '古卷执政官', '普通系', '幻系', 658, '图书守卫者：入场时，若自己的魔力值为1，自己获得双攻+50%。'),
('306', '古卷匣魔像', '普通系', '武系', 650, '构装契约者：入场时，若敌方魔力值为1，自己获得双防+50%。'),
('307', '绒绒', '光系', '虫系', 342, '绒粉星光：攻击时，若敌方血脉是非本系别血脉，技能威力+100%。'),
('308', '小绒茧', '光系', '虫系', 454, '绒粉星光：攻击时，若敌方血脉是非本系别血脉，技能威力+100%。'),
('309', '绒仙子', '光系', '虫系', 569, '绒粉星光：攻击时，若敌方血脉是非本系别血脉，技能威力+100%。'),
('310', '犀角鸟', '光系', NULL, 368, '月光审判：攻击时，若敌方血脉是首领血脉，技能威力+100%。'),
('311', '光纤兽', '光系', NULL, 490, '月光审判：攻击时，若敌方血脉是首领血脉，技能威力+100%。'),
('312', '疾光千兽', '光系', NULL, 612, '月光审判：攻击时，若敌方血脉是首领血脉，技能威力+100%。'),
('313', '果冻', '水系', NULL, 437, '茶多酚：离场后，更换入场的精灵回复20%生命且免疫寄生。'),
('314', '抹茶布丁', '水系', '草系', 546, '茶多酚：离场后，更换入场的精灵回复20%生命且免疫寄生。'),
('315', '椰浆布丁', '水系', '冰系', 562, '吉利丁片：离场后，更换入场的精灵获得双防+20%且免疫冻结。'),
('316', '熔岩布丁', '水系', '火系', 564, '美拉德反应：离场后，更换入场的精灵获得双攻+20%且免疫灼烧。'),
('317', '星尘虫', '虫系', NULL, 307, '契约的形状：根据捕捉所用的咕噜球，入场时获得不同效果。'),
('318', '落星虫', '虫系', NULL, 407, '契约的形状：根据捕捉所用的咕噜球，入场时获得不同效果。'),
('319', '陨星虫', '虫系', NULL, 509, '契约的形状：根据捕捉所用的咕噜球，入场时获得不同效果。'),
('320', '双灯鱼', '水系', '电系', 502, '对流：自己的能耗增加变为能耗降低；能耗降低变为能耗增加。'),
('321', '利灯鱼', '水系', '电系', 626, '对流：自己的能耗增加变为能耗降低；能耗降低变为能耗增加。'),
('322', '月牙雪熊', '冰系', '幻系', 586, '月牙雪糕：使用攻击技能时，敌方每层冻结视为1层额外星陨印记。'),
('323', '嗜光嗡嗡', '恶系', '光系', 473, '血型吸引：敌方每携带一种系别的技能，自己攻击时威力+10。'),
('324', '窃光纹', '恶系', '光系', 592, '血型吸引：敌方每携带一种系别的技能，自己攻击时威力+10。'),
('325', '柴渣虫', '火系', '草系', 462, '煤渣草：在场时，所有灼烧的衰减变为增长。'),
('326', '燃薪虫', '火系', '草系', 579, '煤渣草：在场时，所有灼烧的衰减变为增长。'),
('327', '空空颅', '幽系', NULL, 280, '搜刮：敌方每使用1次【聚能】技能或更换精灵，自己入场时获得魔攻+20%。'),
('328', '夜宿颅', '幽系', NULL, 373, '搜刮：敌方每使用1次【聚能】技能或更换精灵，自己入场时获得魔攻+20%。'),
('329', '夜枭', '幽系', NULL, 464, '搜刮：敌方每使用1次【聚能】技能或更换精灵，自己入场时获得魔攻+20%。'),
('330', '粉粉星', '电系', '幻系', 495, '星地善良：回合结束时，若场上的己方精灵能量等于0，自己立即替换此精灵。'),
('331', '小皮球', '电系', '幻系', 618, '星地善良：回合结束时，若场上的己方精灵能量等于0，自己立即替换此精灵。'),
('332', '贝瑟', '机械系', '火系', 385, '贪心算法：1号位技能获得传动1，且使用后使敌方获得6层灼烧。'),
('333', '贝加尔', '机械系', '火系', 512, '贪心算法：1号位技能获得传动1，且使用后使敌方获得6层灼烧。'),
('334', '贝古斯', '机械系', '火系', 641, '贪心算法：1号位技能获得传动1，且使用后使敌方获得6层灼烧。'),
('335', '粉星仔', '幻系', NULL, 514, '双向光速：在场时，所有回合结束时效果，触发次数+1。'),
('336', '粉耳星兔', '幻系', NULL, 642, '双向光速：在场时，所有回合结束时效果，触发次数+1。'),
('337', '落陨星兔', '幻系', '幽系', 637, '陨落：在场时，双方回合结束时触发的效果，触发次数-1。'),
('338', '布瓜蝌', '幻系', NULL, 442, '张弛有度：周末时自己获得双攻+40%，其他时间获得双防+40%。'),
('339', '上岸蛙', '幻系', NULL, 554, '张弛有度：周末时自己获得双攻+40%，其他时间获得双防+40%。'),
('340', '火红尾', '火系', NULL, 511, '天通地明：攻击时，若敌方是污染血脉，技能威力+100%。'),
('341', '雅丹鬃', '火系', NULL, 639, '天通地明：攻击时，若敌方是污染血脉，技能威力+100%。'),
('342', '春团', '草系', NULL, 341, '系统发育：获得能量或生命时，会将等量的能量或生命随机分配给场下的精灵。'),
('343', '春兔', '草系', NULL, 455, '系统发育：获得能量或生命时，会将等量的能量或生命随机分配给场下的精灵。'),
('344', '春花兔', '草系', NULL, 557, '系统发育：获得能量或生命时，会将等量的能量或生命随机分配给场下的精灵。'),
('345', '幽星光', '幻系', NULL, 319, '守望星：触发星陨印记时仅消耗一半层数，仍造成满层伤害。'),
('346', '耀星光', '幻系', '翼系', 425, '守望星：触发星陨印记时仅消耗一半层数，仍造成满层伤害。'),
('347', '暮星辰', '幻系', '翼系', 532, '守望星：触发星陨印记时仅消耗一半层数，仍造成满层伤害。')
"""

SQL_INSERT_STATS = """
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 120, 80, 105, 80, 105, 92 FROM pokemon WHERE national_number='001';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 65, 53, 59, 53, 62, 54 FROM pokemon WHERE national_number='002';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 77, 75, 77, 79, 44 FROM pokemon WHERE national_number='003';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 96, 94, 96, 99, 55 FROM pokemon WHERE national_number='004';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 70, 84, 56, 37, 43, 78 FROM pokemon WHERE national_number='005';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 111, 75, 49, 58, 104 FROM pokemon WHERE national_number='006';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 117, 139, 94, 61, 72, 130 FROM pokemon WHERE national_number='007';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 51, 43, 58, 84, 74, 51 FROM pokemon WHERE national_number='008';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 46, 102, 75, 106, 68 FROM pokemon WHERE national_number='009';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 125, 58, 127, 94, 132, 85 FROM pokemon WHERE national_number='010';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 136, 95, 55, 35, 45, 105 FROM pokemon WHERE national_number='011';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 28, 64, 72, 81, 45 FROM pokemon WHERE national_number='012';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 37, 85, 96, 107, 60 FROM pokemon WHERE national_number='013';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 46, 107, 120, 134, 75 FROM pokemon WHERE national_number='014';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 66, 72, 29, 49, 66 FROM pokemon WHERE national_number='015';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 89, 96, 39, 65, 88 FROM pokemon WHERE national_number='016';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 111, 120, 48, 81, 110 FROM pokemon WHERE national_number='017';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 56, 77, 58, 26, 49, 69 FROM pokemon WHERE national_number='018';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 103, 86, 44, 59, 92 FROM pokemon WHERE national_number='019';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 128, 108, 55, 74, 115 FROM pokemon WHERE national_number='020';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 59, 62, 59, 82, 45 FROM pokemon WHERE national_number='021';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 79, 83, 79, 109, 60 FROM pokemon WHERE national_number='022';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 98, 103, 98, 136, 75 FROM pokemon WHERE national_number='023';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 69, 54, 65, 53, 45, 57 FROM pokemon WHERE national_number='024';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 72, 87, 71, 60, 76 FROM pokemon WHERE national_number='025';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 115, 89, 109, 89, 75, 95 FROM pokemon WHERE national_number='026';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 81, 95, 29, 90, 42 FROM pokemon WHERE national_number='027';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 96, 108, 129, 39, 120, 56 FROM pokemon WHERE national_number='028';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 120, 135, 159, 49, 150, 70 FROM pokemon WHERE national_number='029';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 112, 58, 44, 43, 84 FROM pokemon WHERE national_number='030';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 108, 140, 73, 55, 54, 105 FROM pokemon WHERE national_number='031';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 32, 28, 40, 28, 40, 60 FROM pokemon WHERE national_number='032';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 42, 37, 53, 37, 53, 80 FROM pokemon WHERE national_number='033';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 53, 46, 66, 46, 66, 100 FROM pokemon WHERE national_number='034';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 96, 65, 96, 123, 80 FROM pokemon WHERE national_number='035';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 57, 60, 57, 60, 48 FROM pokemon WHERE national_number='036';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 97, 77, 81, 77, 81, 64 FROM pokemon WHERE national_number='037';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 121, 96, 101, 96, 101, 80 FROM pokemon WHERE national_number='038';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 77, 102, 81, 75, 52 FROM pokemon WHERE national_number='039';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 99, 96, 128, 101, 94, 65 FROM pokemon WHERE national_number='040';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 69, 73, 69, 57, 48 FROM pokemon WHERE national_number='041';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 92, 97, 92, 76, 64 FROM pokemon WHERE national_number='042';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 115, 121, 115, 95, 80 FROM pokemon WHERE national_number='043';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 44, 45, 49, 12, 40, 78 FROM pokemon WHERE national_number='044';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 59, 60, 65, 16, 53, 104 FROM pokemon WHERE national_number='045';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 75, 81, 20, 67, 130 FROM pokemon WHERE national_number='046';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 68, 103, 81, 37, 66, 96 FROM pokemon WHERE national_number='047';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 128, 101, 46, 82, 120 FROM pokemon WHERE national_number='048';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 69, 50, 67, 47, 52, 48 FROM pokemon WHERE national_number='049';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 67, 89, 63, 70, 64 FROM pokemon WHERE national_number='050';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 114, 84, 111, 79, 87, 80 FROM pokemon WHERE national_number='051';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 110, 29, 71, 82, 83, 84 FROM pokemon WHERE national_number='052';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 137, 36, 89, 102, 104, 105 FROM pokemon WHERE national_number='053';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 55, 30, 59, 72, 81, 69 FROM pokemon WHERE national_number='054';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 40, 78, 96, 108, 92 FROM pokemon WHERE national_number='055';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 50, 98, 120, 135, 115 FROM pokemon WHERE national_number='056';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 40, 60, 106, 74, 92 FROM pokemon WHERE national_number='057';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 113, 50, 75, 133, 93, 115 FROM pokemon WHERE national_number='058';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 70, 79, 70, 82, 97, 115 FROM pokemon WHERE national_number='059';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 95, 56, 70, 25, 41, 51 FROM pokemon WHERE national_number='060';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 126, 74, 94, 33, 54, 68 FROM pokemon WHERE national_number='061';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 158, 93, 117, 41, 68, 85 FROM pokemon WHERE national_number='062';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 60, 64, 44, 66, 63, 51 FROM pokemon WHERE national_number='063';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 80, 85, 59, 88, 84, 68 FROM pokemon WHERE national_number='064';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 107, 73, 110, 105, 85 FROM pokemon WHERE national_number='065';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 47, 49, 55, 49, 57, 75 FROM pokemon WHERE national_number='066';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 62, 66, 73, 66, 76, 100 FROM pokemon WHERE national_number='067';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 82, 91, 82, 95, 125 FROM pokemon WHERE national_number='068';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 99, 103, 94, 78, 52 FROM pokemon WHERE national_number='069';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 123, 129, 117, 97, 65 FROM pokemon WHERE national_number='070';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 73, 76, 71, 76, 72 FROM pokemon WHERE national_number='071';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 91, 95, 89, 95, 90 FROM pokemon WHERE national_number='072';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 94, 81, 38, 66, 45 FROM pokemon WHERE national_number='073';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 115, 125, 108, 51, 88, 60 FROM pokemon WHERE national_number='074';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 144, 157, 135, 64, 110, 75 FROM pokemon WHERE national_number='075';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 71, 25, 46, 59, 66, 60 FROM pokemon WHERE national_number='076';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 94, 33, 61, 79, 88, 80 FROM pokemon WHERE national_number='077';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 118, 41, 76, 99, 111, 100 FROM pokemon WHERE national_number='078';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 49, 77, 116, 115, 60 FROM pokemon WHERE national_number='079';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 60, 81, 72, 85, 88, 108 FROM pokemon WHERE national_number='080';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 101, 90, 106, 110, 135 FROM pokemon WHERE national_number='081';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 87, 32, 27, 29, 27, 26 FROM pokemon WHERE national_number='082';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 116, 43, 36, 39, 36, 35 FROM pokemon WHERE national_number='083';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 145, 54, 45, 49, 45, 44 FROM pokemon WHERE national_number='084';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 60, 69, 62, 63, 51, 69 FROM pokemon WHERE national_number='085';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 80, 92, 83, 84, 68, 92 FROM pokemon WHERE national_number='086';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 115, 104, 105, 85, 115 FROM pokemon WHERE national_number='087';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 57, 52, 83, 58, 69 FROM pokemon WHERE national_number='088';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 76, 110, 69, 78, 92 FROM pokemon WHERE national_number='089';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 125, 95, 138, 86, 97, 115 FROM pokemon WHERE national_number='090';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 132, 93, 130, 87, 90, 120 FROM pokemon WHERE national_number='091';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 67, 65, 91, 72, 105 FROM pokemon WHERE national_number='092';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 35, 87, 89, 111, 72 FROM pokemon WHERE national_number='093';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 99, 43, 109, 112, 139, 90 FROM pokemon WHERE national_number='094';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 108, 97, 141, 79, 70 FROM pokemon WHERE national_number='095';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 58, 68, 66, 61, 53, 72 FROM pokemon WHERE national_number='096';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 91, 88, 81, 71, 96 FROM pokemon WHERE national_number='097';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 97, 114, 101, 110, 89, 120 FROM pokemon WHERE national_number='098';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 40, 43, 50, 57, 60 FROM pokemon WHERE national_number='099';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 97, 53, 67, 57, 75, 80 FROM pokemon WHERE national_number='100';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 122, 67, 84, 72, 94, 100 FROM pokemon WHERE national_number='101';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 52, 68, 56, 20, 53, 81 FROM pokemon WHERE national_number='102';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 70, 91, 75, 27, 70, 108 FROM pokemon WHERE national_number='103';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 87, 113, 94, 34, 88, 135 FROM pokemon WHERE national_number='104';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 64, 95, 67, 47, 42, 45 FROM pokemon WHERE national_number='105';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 127, 89, 62, 56, 60 FROM pokemon WHERE national_number='106';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 107, 159, 112, 78, 70, 75 FROM pokemon WHERE national_number='107';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 54, 46, 63, 46, 63, 75 FROM pokemon WHERE national_number='108';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 61, 84, 61, 84, 100 FROM pokemon WHERE national_number='109';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 77, 105, 77, 105, 125 FROM pokemon WHERE national_number='110';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 76, 79, 101, 79, 56, 76 FROM pokemon WHERE national_number='111';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 95, 99, 126, 99, 70, 95 FROM pokemon WHERE national_number='112';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 64, 54, 69, 57, 71, 51 FROM pokemon WHERE national_number='113';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 72, 92, 76, 95, 68 FROM pokemon WHERE national_number='114';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 90, 115, 95, 119, 85 FROM pokemon WHERE national_number='115';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 48, 62, 129, 74, 84 FROM pokemon WHERE national_number='116';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 99, 61, 77, 161, 92, 105 FROM pokemon WHERE national_number='117';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 56, 15, 63, 65, 55, 72 FROM pokemon WHERE national_number='118';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 19, 84, 87, 73, 96 FROM pokemon WHERE national_number='119';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 24, 105, 109, 91, 120 FROM pokemon WHERE national_number='120';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 121, 72, 54, 130, 95, 56 FROM pokemon WHERE national_number='121';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 152, 91, 67, 163, 119, 70 FROM pokemon WHERE national_number='122';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 87, 84, 84, 56, 104 FROM pokemon WHERE national_number='123';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 97, 109, 105, 105, 70, 130 FROM pokemon WHERE national_number='124';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 47, 53, 82, 53, 66, 54 FROM pokemon WHERE national_number='125';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 70, 109, 70, 88, 72 FROM pokemon WHERE national_number='126';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 88, 136, 88, 110, 90 FROM pokemon WHERE national_number='127';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 38, 30, 41, 60, 36 FROM pokemon WHERE national_number='128';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 99, 50, 40, 55, 80, 48 FROM pokemon WHERE national_number='129';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 124, 63, 50, 69, 100, 60 FROM pokemon WHERE national_number='130';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 115, 114, 91, 45, 63, 120 FROM pokemon WHERE national_number='131';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 45, 59, 101, 87, 100 FROM pokemon WHERE national_number='132';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 94, 56, 73, 126, 109, 125 FROM pokemon WHERE national_number='133';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 97, 104, 83, 47, 62, 36 FROM pokemon WHERE national_number='134';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 130, 139, 111, 63, 83, 48 FROM pokemon WHERE national_number='135';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 162, 174, 139, 79, 104, 60 FROM pokemon WHERE national_number='136';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 98, 95, 88, 33, 81, 68 FROM pokemon WHERE national_number='137';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 123, 119, 110, 41, 101, 85 FROM pokemon WHERE national_number='138';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 56, 67, 63, 63, 67, 69 FROM pokemon WHERE national_number='139';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 90, 84, 90, 84, 92 FROM pokemon WHERE national_number='140';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 94, 112, 105, 112, 105, 115 FROM pokemon WHERE national_number='141';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 62, 39, 59, 78, 54 FROM pokemon WHERE national_number='142';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 104, 83, 52, 78, 104, 72 FROM pokemon WHERE national_number='143';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 130, 103, 66, 98, 130, 90 FROM pokemon WHERE national_number='144';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 82, 84, 109, 78, 109, 60 FROM pokemon WHERE national_number='145';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 103, 105, 136, 97, 136, 75 FROM pokemon WHERE national_number='146';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 69, 52, 50, 52, 64, 60 FROM pokemon WHERE national_number='147';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 70, 67, 70, 86, 80 FROM pokemon WHERE national_number='148';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 115, 87, 84, 87, 107, 100 FROM pokemon WHERE national_number='149';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 65, 77, 65, 50, 75 FROM pokemon WHERE national_number='150';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 105, 87, 102, 87, 66, 100 FROM pokemon WHERE national_number='151';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 132, 109, 128, 109, 83, 125 FROM pokemon WHERE national_number='152';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 83, 77, 34, 60, 63 FROM pokemon WHERE national_number='153';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 84, 111, 102, 46, 80, 84 FROM pokemon WHERE national_number='154';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 105, 139, 128, 57, 100, 105 FROM pokemon WHERE national_number='155';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 82, 31, 53, 66, 78, 48 FROM pokemon WHERE national_number='156';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 110, 41, 70, 89, 104, 64 FROM pokemon WHERE national_number='157';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 137, 51, 88, 111, 130, 80 FROM pokemon WHERE national_number='158';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 66, 62, 62, 62, 63 FROM pokemon WHERE national_number='159';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 84, 88, 83, 83, 83, 84 FROM pokemon WHERE national_number='160';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 105, 110, 103, 104, 103, 105 FROM pokemon WHERE national_number='161';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 113, 93, 125, 93, 125, 100 FROM pokemon WHERE national_number='162';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 106, 89, 101, 76, 76 FROM pokemon WHERE national_number='163';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 132, 111, 126, 95, 95 FROM pokemon WHERE national_number='164';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 61, 69, 64, 39, 33, 72 FROM pokemon WHERE national_number='165';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 82, 92, 86, 51, 44, 96 FROM pokemon WHERE national_number='166';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 102, 116, 107, 64, 55, 120 FROM pokemon WHERE national_number='167';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 55, 37, 55, 37, 55, 66 FROM pokemon WHERE national_number='168';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 74, 49, 73, 49, 73, 88 FROM pokemon WHERE national_number='169';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 61, 91, 61, 91, 110 FROM pokemon WHERE national_number='170';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 59, 87, 59, 66, 42 FROM pokemon WHERE national_number='171';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 78, 116, 78, 88, 56 FROM pokemon WHERE national_number='172';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 98, 146, 98, 110, 70 FROM pokemon WHERE national_number='173';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 61, 70, 57, 57, 42 FROM pokemon WHERE national_number='174';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 119, 81, 93, 76, 76, 56 FROM pokemon WHERE national_number='175';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 149, 102, 116, 95, 95, 70 FROM pokemon WHERE national_number='176';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 71, 90, 71, 90, 80, 92 FROM pokemon WHERE national_number='177';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 112, 89, 112, 100, 115 FROM pokemon WHERE national_number='178';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 79, 66, 24, 50, 92 FROM pokemon WHERE national_number='179';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 116, 98, 83, 29, 63, 115 FROM pokemon WHERE national_number='180';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 91, 89, 87, 62, 80 FROM pokemon WHERE national_number='181';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 113, 111, 109, 77, 100 FROM pokemon WHERE national_number='182';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 109, 27, 76, 76, 88, 84 FROM pokemon WHERE national_number='183';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 136, 34, 95, 95, 110, 105 FROM pokemon WHERE national_number='184';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 68, 61, 49, 64, 74, 54 FROM pokemon WHERE national_number='185';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 91, 81, 66, 86, 99, 72 FROM pokemon WHERE national_number='186';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 114, 102, 82, 107, 124, 90 FROM pokemon WHERE national_number='187';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 100, 70, 36, 56, 100 FROM pokemon WHERE national_number='188';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 126, 88, 45, 69, 125 FROM pokemon WHERE national_number='189';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 94, 116, 38, 77, 75 FROM pokemon WHERE national_number='190';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 126, 87, 90, 87, 72, 85 FROM pokemon WHERE national_number='191';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 84, 82, 84, 75, 90 FROM pokemon WHERE national_number='192';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 37, 67, 93, 90, 92 FROM pokemon WHERE national_number='193';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 46, 84, 116, 112, 115 FROM pokemon WHERE national_number='194';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 52, 60, 68, 64, 79, 57 FROM pokemon WHERE national_number='195';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 69, 80, 91, 86, 105, 76 FROM pokemon WHERE national_number='196';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 100, 113, 107, 132, 95 FROM pokemon WHERE national_number='197';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 48, 70, 68, 64, 68, 66 FROM pokemon WHERE national_number='198';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 64, 93, 90, 86, 90, 88 FROM pokemon WHERE national_number='199';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 117, 113, 107, 113, 110 FROM pokemon WHERE national_number='200';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 232, 73, 110, 73, 90, 52 FROM pokemon WHERE national_number='201';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 290, 91, 138, 91, 113, 65 FROM pokemon WHERE national_number='202';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 73, 55, 152, 79, 72 FROM pokemon WHERE national_number='203';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 91, 69, 190, 99, 90 FROM pokemon WHERE national_number='204';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 80, 62, 80, 78, 100 FROM pokemon WHERE national_number='205';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 83, 100, 78, 100, 97, 125 FROM pokemon WHERE national_number='206';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 64, 49, 51, 49, 50, 72 FROM pokemon WHERE national_number='207';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 85, 68, 65, 67, 96 FROM pokemon WHERE national_number='208';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 81, 85, 81, 84, 120 FROM pokemon WHERE national_number='209';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 103, 122, 103, 122, 64 FROM pokemon WHERE national_number='210';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 138, 129, 153, 129, 153, 80 FROM pokemon WHERE national_number='211';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 63, 64, 63, 91, 80 FROM pokemon WHERE national_number='212';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 79, 80, 79, 114, 100 FROM pokemon WHERE national_number='213';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 80, 117, 74, 110, 59, 92 FROM pokemon WHERE national_number='214';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 147, 93, 137, 74, 115 FROM pokemon WHERE national_number='215';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 70, 81, 29, 56, 39 FROM pokemon WHERE national_number='216';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 84, 94, 108, 39, 74, 52 FROM pokemon WHERE national_number='217';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 105, 117, 135, 49, 93, 65 FROM pokemon WHERE national_number='218';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 118, 82, 103, 89, 147, 105 FROM pokemon WHERE national_number='219';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 58, 96, 148, 120, 110 FROM pokemon WHERE national_number='220';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 64, 73, 82, 26, 70, 30 FROM pokemon WHERE national_number='221';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 98, 109, 34, 93, 40 FROM pokemon WHERE national_number='222';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 122, 136, 43, 116, 50 FROM pokemon WHERE national_number='223';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 66, 91, 73, 24, 63, 92 FROM pokemon WHERE national_number='224';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 83, 114, 91, 31, 79, 115 FROM pokemon WHERE national_number='225';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 55, 59, 65, 20, 47, 72 FROM pokemon WHERE national_number='226';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 79, 86, 27, 63, 96 FROM pokemon WHERE national_number='227';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 99, 108, 34, 79, 120 FROM pokemon WHERE national_number='228';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 99, 98, 38, 74, 72 FROM pokemon WHERE national_number='229';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 92, 124, 122, 48, 92, 90 FROM pokemon WHERE national_number='230';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 56, 38, 67, 38, 52, 69 FROM pokemon WHERE national_number='231';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 51, 90, 51, 70, 92 FROM pokemon WHERE national_number='232';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 94, 63, 112, 63, 87, 115 FROM pokemon WHERE national_number='233';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 72, 67, 42, 72, 55, 60 FROM pokemon WHERE national_number='234';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 96, 90, 56, 95, 74, 80 FROM pokemon WHERE national_number='235';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 113, 112, 79, 110, 92, 105 FROM pokemon WHERE national_number='236';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 80, 80, 78, 65, 84 FROM pokemon WHERE national_number='237';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 125, 100, 100, 98, 81, 105 FROM pokemon WHERE national_number='238';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 45, 70, 67, 74, 70, 75 FROM pokemon WHERE national_number='239';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 60, 93, 89, 99, 93, 100 FROM pokemon WHERE national_number='240';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 116, 112, 123, 116, 125 FROM pokemon WHERE national_number='241';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 68, 92, 83, 92, 90, 92 FROM pokemon WHERE national_number='242';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 115, 104, 115, 112, 115 FROM pokemon WHERE national_number='243';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 108, 30, 75, 68, 109, 76 FROM pokemon WHERE national_number='244';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 134, 37, 93, 85, 136, 95 FROM pokemon WHERE national_number='245';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 44, 56, 39, 50, 48, 75 FROM pokemon WHERE national_number='246';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 59, 74, 52, 67, 64, 100 FROM pokemon WHERE national_number='247';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 93, 65, 83, 81, 125 FROM pokemon WHERE national_number='248';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 97, 86, 43, 67, 36 FROM pokemon WHERE national_number='249';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 133, 130, 115, 57, 89, 48 FROM pokemon WHERE national_number='250';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 167, 162, 143, 72, 111, 60 FROM pokemon WHERE national_number='251';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 44, 60, 68, 16, 53, 54 FROM pokemon WHERE national_number='252';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 58, 81, 91, 22, 70, 72 FROM pokemon WHERE national_number='253';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 73, 101, 114, 27, 88, 90 FROM pokemon WHERE national_number='254';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 28, 60, 73, 76, 54 FROM pokemon WHERE national_number='255';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 90, 38, 80, 98, 101, 72 FROM pokemon WHERE national_number='256';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 112, 47, 100, 122, 127, 90 FROM pokemon WHERE national_number='257';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 80, 95, 70, 49, 42, 33 FROM pokemon WHERE national_number='258';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 107, 126, 93, 66, 56, 44 FROM pokemon WHERE national_number='259';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 134, 158, 116, 82, 70, 55 FROM pokemon WHERE national_number='260';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 88, 55, 79, 8, 67, 80 FROM pokemon WHERE national_number='261';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 110, 68, 99, 10, 84, 100 FROM pokemon WHERE national_number='262';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 62, 81, 76, 32, 60, 51 FROM pokemon WHERE national_number='263';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 82, 108, 101, 43, 80, 68 FROM pokemon WHERE national_number='264';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 103, 135, 127, 54, 101, 85 FROM pokemon WHERE national_number='265';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 65, 79, 55, 79, 52, 66 FROM pokemon WHERE national_number='266';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 106, 74, 106, 70, 88 FROM pokemon WHERE national_number='267';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 108, 132, 92, 132, 87, 110 FROM pokemon WHERE national_number='268';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 121, 144, 92, 58, 70, 95 FROM pokemon WHERE national_number='269';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 35, 84, 89, 104, 92 FROM pokemon WHERE national_number='270';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 101, 43, 105, 111, 130, 115 FROM pokemon WHERE national_number='271';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 116, 85, 109, 85, 145 FROM pokemon WHERE national_number='272';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 129, 40, 119, 115, 135, 50 FROM pokemon WHERE national_number='273';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 65, 31, 48, 74, 67, 36 FROM pokemon WHERE national_number='274';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 86, 42, 64, 99, 90, 48 FROM pokemon WHERE national_number='275';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 108, 52, 80, 124, 112, 60 FROM pokemon WHERE national_number='276';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 66, 71, 61, 31, 42, 66 FROM pokemon WHERE national_number='277';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 88, 95, 82, 41, 56, 88 FROM pokemon WHERE national_number='278';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 110, 119, 102, 51, 70, 110 FROM pokemon WHERE national_number='279';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 103, 84, 105, 34, 79, 56 FROM pokemon WHERE national_number='280';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 129, 105, 131, 42, 99, 70 FROM pokemon WHERE national_number='281';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 120, 124, 39, 113, 130 FROM pokemon WHERE national_number='282';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 98, 71, 97, 31, 61, 60 FROM pokemon WHERE national_number='283';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 122, 88, 121, 39, 77, 75 FROM pokemon WHERE national_number='284';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 139, 116, 139, 111, 139, 52 FROM pokemon WHERE national_number='285';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 174, 144, 173, 139, 173, 65 FROM pokemon WHERE national_number='286';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 99, 89, 87, 33, 71, 76 FROM pokemon WHERE national_number='287';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 124, 112, 109, 41, 88, 95 FROM pokemon WHERE national_number='288';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 96, 109, 84, 40, 65, 48 FROM pokemon WHERE national_number='289';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 120, 137, 104, 50, 81, 60 FROM pokemon WHERE national_number='290';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 64, 81, 17, 59, 108 FROM pokemon WHERE national_number='291';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 84, 80, 101, 21, 74, 135 FROM pokemon WHERE national_number='292';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 78, 76, 79, 34, 52, 60 FROM pokemon WHERE national_number='293';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 104, 102, 105, 46, 70, 80 FROM pokemon WHERE national_number='294';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 130, 127, 131, 57, 87, 100 FROM pokemon WHERE national_number='295';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 85, 80, 93, 27, 79, 88 FROM pokemon WHERE national_number='296';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 106, 100, 116, 34, 99, 110 FROM pokemon WHERE national_number='297';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 109, 105, 113, 37, 97, 115 FROM pokemon WHERE national_number='298';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 61, 32, 56, 78, 72, 72 FROM pokemon WHERE national_number='299';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 42, 75, 104, 96, 96 FROM pokemon WHERE national_number='300';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 101, 53, 94, 131, 120, 120 FROM pokemon WHERE national_number='301';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 160, 100, 67, 76, 105 FROM pokemon WHERE national_number='302';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 75, 48, 75, 73, 57 FROM pokemon WHERE national_number='303';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 89, 100, 64, 100, 98, 76 FROM pokemon WHERE national_number='304';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 111, 125, 80, 125, 122, 95 FROM pokemon WHERE national_number='305';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 114, 109, 134, 109, 89, 95 FROM pokemon WHERE national_number='306';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 58, 42, 49, 44, 80, 69 FROM pokemon WHERE national_number='307';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 77, 56, 65, 58, 106, 92 FROM pokemon WHERE national_number='308';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 96, 71, 81, 73, 133, 115 FROM pokemon WHERE national_number='309';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 88, 67, 40, 44, 66 FROM pokemon WHERE national_number='310';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 83, 117, 90, 54, 58, 88 FROM pokemon WHERE national_number='311';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 104, 146, 112, 67, 73, 110 FROM pokemon WHERE national_number='312';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 26, 75, 81, 78, 96 FROM pokemon WHERE national_number='313';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 101, 32, 94, 101, 98, 120 FROM pokemon WHERE national_number='314';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 133, 34, 81, 89, 105, 120 FROM pokemon WHERE national_number='315';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 128, 87, 112, 33, 84, 120 FROM pokemon WHERE national_number='316';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 49, 47, 46, 47, 58, 60 FROM pokemon WHERE national_number='317';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 65, 62, 61, 62, 77, 80 FROM pokemon WHERE national_number='318';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 78, 76, 78, 96, 100 FROM pokemon WHERE national_number='319';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 102, 55, 57, 111, 93, 84 FROM pokemon WHERE national_number='320';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 128, 68, 71, 138, 116, 105 FROM pokemon WHERE national_number='321';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 126, 97, 141, 39, 103, 80 FROM pokemon WHERE national_number='322';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 75, 83, 50, 83, 90, 92 FROM pokemon WHERE national_number='323';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 104, 63, 104, 113, 115 FROM pokemon WHERE national_number='324';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 108, 96, 82, 38, 58, 80 FROM pokemon WHERE national_number='325';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 135, 120, 103, 48, 73, 100 FROM pokemon WHERE national_number='326';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 70, 7, 54, 37, 64, 48 FROM pokemon WHERE national_number='327';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 94, 9, 72, 49, 85, 64 FROM pokemon WHERE national_number='328';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 117, 10, 90, 61, 106, 80 FROM pokemon WHERE national_number='329';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 54, 57, 102, 101, 88 FROM pokemon WHERE national_number='330';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 116, 68, 71, 127, 126, 110 FROM pokemon WHERE national_number='331';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 46, 51, 78, 98, 33 FROM pokemon WHERE national_number='332';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 105, 61, 68, 104, 130, 44 FROM pokemon WHERE national_number='333';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 132, 76, 85, 130, 163, 55 FROM pokemon WHERE national_number='334';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 80, 63, 58, 119, 102, 92 FROM pokemon WHERE national_number='335';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 100, 79, 73, 148, 127, 115 FROM pokemon WHERE national_number='336';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 93, 61, 87, 125, 141, 130 FROM pokemon WHERE national_number='337';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 91, 84, 81, 35, 55, 96 FROM pokemon WHERE national_number='338';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 114, 106, 101, 44, 69, 120 FROM pokemon WHERE national_number='339';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 67, 56, 70, 129, 89, 100 FROM pokemon WHERE national_number='340';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 83, 70, 88, 162, 111, 125 FROM pokemon WHERE national_number='341';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 48, 51, 65, 57, 57, 63 FROM pokemon WHERE national_number='342';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 63, 68, 87, 76, 77, 84 FROM pokemon WHERE national_number='343';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 79, 85, 103, 95, 90, 105 FROM pokemon WHERE national_number='344';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 49, 21, 48, 63, 63, 75 FROM pokemon WHERE national_number='345';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 65, 28, 64, 84, 84, 100 FROM pokemon WHERE national_number='346';
INSERT INTO pokemon_stats (pokemon_id, hp, attack, defense, sp_attack, sp_defense, speed)
SELECT id, 81, 35, 80, 106, 105, 125 FROM pokemon WHERE national_number='347';
"""

def init_database():
    print("正在连接 PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    print("创建表（重建）...")
    cursor.execute(SQL_CREATE_TABLES)
    print("插入精灵基本信息...")
    cursor.execute(SQL_INSERT_POKEMON)

    print("插入精灵种族值...")
    # 逐条执行 stats 插入
    cursor.execute(SQL_INSERT_STATS)

    cursor.close()
    conn.close()
    print(f"✅ 精灵数据库初始化完成！共347只精灵。")

if __name__ == "__main__":
    init_database()