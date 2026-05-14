#!/usr/bin/env python3
"""
AI Exercise Recommender — AI 运动方案推荐

模拟大模型对运动方案的推理分析，展示：
1. 个体化体能评估
2. 渐进式训练计划设计
3. 安全风险评估

使用方式：
    python exercise_recommender.py
"""

import math


# ============================================================
# 知识库
# ============================================================

EXERCISE_LIBRARY = {
    "有氧": [
        {"name": "快走", "intensity": "low", "kcal_per_min": 4, "risk": "low", "equipment": "无"},
        {"name": "慢跑", "intensity": "moderate", "kcal_per_min": 7, "risk": "medium", "equipment": "跑鞋"},
        {"name": "游泳", "intensity": "moderate", "kcal_per_min": 8, "risk": "low", "equipment": "泳池"},
        {"name": "骑行", "intensity": "moderate", "kcal_per_min": 6, "risk": "low", "equipment": "自行车"},
        {"name": "跳绳", "intensity": "high", "kcal_per_min": 12, "risk": "high", "equipment": "跳绳"},
    ],
    "力量": [
        {"name": "深蹲", "target": "腿部", "level": "beginner", "equipment": "无"},
        {"name": "俯卧撑", "target": "胸部", "level": "beginner", "equipment": "无"},
        {"name": "引体向上", "target": "背部", "level": "advanced", "equipment": "单杠"},
        {"name": "平板支撑", "target": "核心", "level": "beginner", "equipment": "无"},
        {"name": "划船", "target": "背部", "level": "intermediate", "equipment": "弹力带/哑铃"},
        {"name": "弓步蹲", "target": "腿部", "level": "beginner", "equipment": "无"},
        {"name": "哑铃推举", "target": "肩部", "level": "intermediate", "equipment": "哑铃"},
    ],
}

WEEKLY_FREQUENCY_RECOMMENDATIONS = {
    "weight_loss": {"cardio_days": 3, "strength_days": 2, "rest_days": 2},
    "maintain": {"cardio_days": 2, "strength_days": 2, "rest_days": 3},
    "muscle_gain": {"cardio_days": 1, "strength_days": 4, "rest_days": 2},
}


# ============================================================
# 评估函数
# ============================================================

def assess_fitness_level(bmi, age, exercise_freq, experience):
    """
    综合体能评估

    评估维度：
    1. BMI 基础健康
    2. 年龄因素
    3. 运动频率
    4. 运动经验
    """
    score = 0

    # BMI (最高3分)
    if 18.5 <= bmi < 24:
        score += 3
    elif 24 <= bmi < 28:
        score += 1
    else:
        score += 0

    # 年龄 (最高2分)
    if age <= 30:
        score += 2
    elif age <= 45:
        score += 1
    else:
        score += 0

    # 运动频率 (最高3分)
    if exercise_freq >= 4:
        score += 3
    elif exercise_freq >= 2:
        score += 2
    elif exercise_freq >= 1:
        score += 1

    # 经验 (最高2分)
    exp_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
    score += exp_map.get(experience, 0)

    # 综合评级
    if score >= 8:
        return "高级"
    elif score >= 5:
        return "中级"
    else:
        return "初级"


def estimate_target_heart_rate(age, fitness_level):
    """
    估算目标心率区间

    Karvonen 公式：
    目标心率 = (220 - age - 静息心率) × 强度 + 静息心率
    """
    resting_hr = 70  # 默认静息心率
    max_hr = 220 - age

    zones = {
        "初级": {"warmup": (0.5, 0.6), "fat_burn": (0.6, 0.7), "cardio": (0.7, 0.8)},
        "中级": {"warmup": (0.5, 0.6), "fat_burn": (0.6, 0.7), "cardio": (0.7, 0.85)},
        "高级": {"warmup": (0.5, 0.6), "fat_burn": (0.6, 0.7), "cardio": (0.7, 0.9)},
    }

    user_zones = zones.get(fitness_level, zones["初级"])
    heart_rate_zones = {}
    for zone_name, (low_pct, high_pct) in user_zones.items():
        low = int((max_hr - resting_hr) * low_pct + resting_hr)
        high = int((max_hr - resting_hr) * high_pct + resting_hr)
        heart_rate_zones[zone_name] = (low, high)

    max_target = int((max_hr - resting_hr) * 0.85 + resting_hr)

    return heart_rate_zones, max_target


# ============================================================
# 方案生成
# ============================================================

def generate_exercise_plan(user_data, fitness_level):
    """
    根据评估结果生成运动计划
    """
    goal = user_data.get("goal", "weight_loss")
    freq = WEEKLY_FREQUENCY_RECOMMENDATIONS.get(goal, WEEKLY_FREQUENCY_RECOMMENDATIONS["weight_loss"])
    age = user_data.get("age", 30)

    hr_zones, max_target = estimate_target_heart_rate(age, fitness_level)

    # 有氧运动方案
    if fitness_level == "初级":
        cardio_duration = 30  # 分钟
        cardio_type = "快走"
        intensity = "低强度"
    elif fitness_level == "中级":
        cardio_duration = 40
        cardio_type = "慢跑或骑行"
        intensity = "中强度"
    else:
        cardio_duration = 45
        cardio_type = "游泳或跑步"
        intensity = "中高强度"

    # 力量训练方案
    beginner_exercises = ["深蹲 3×12", "俯卧撑 3×10", "平板支撑 3×30s", "弓步蹲 3×10/侧"]
    intermediate_exercises = ["深蹲 4×12", "俯卧撑 4×12", "划船 4×12", "哑铃推举 4×10", "平板支撑 4×45s"]
    advanced_exercises = ["负重深蹲 5×8", "俯卧撑 5×15", "引体向上 5×8", "划船 5×12", "哑铃推举 5×10", "平板支撑 5×60s"]

    strength_exercises = {
        "初级": beginner_exercises,
        "中级": intermediate_exercises,
        "高级": advanced_exercises,
    }

    return {
        "fitness_level": fitness_level,
        "cardio": {
            "days_per_week": freq["cardio_days"],
            "type": cardio_type,
            "duration_min": cardio_duration,
            "intensity": intensity,
            "hr_zone": hr_zones,
            "hr_max_target": max_target,
        },
        "strength": {
            "days_per_week": freq["strength_days"],
            "exercises": strength_exercises.get(fitness_level, beginner_exercises),
        },
        "rest_days": freq["rest_days"],
    }


def format_exercise_plan(plan, user_data):
    """格式化输出运动方案"""
    lines = []
    lines.append("=" * 55)
    lines.append("  AI 运动推荐方案")
    lines.append("=" * 55)
    lines.append("")

    gender = user_data.get("gender", "M")
    age = user_data.get("age", 30)
    weight = user_data.get("weight_kg", 70)

    goal_labels = {
        "weight_loss": "减脂",
        "weight_loss_fast": "快速减脂",
        "maintain": "体重维持",
        "muscle_gain": "增肌",
    }
    goal_label = goal_labels.get(user_data.get("goal", "weight_loss"), "减脂")

    lines.append(f"📋 用户评估")
    lines.append(f"  性别: {'男' if gender == 'M' else '女'} | 年龄: {age}岁 | 体重: {weight}kg")
    lines.append(f"  体能等级: {plan['fitness_level']} | 目标: {goal_label}")
    lines.append("")

    lines.append(f"🏃 有氧训练")
    lines.append(f"  频率: {plan['cardio']['days_per_week']}次/周")
    lines.append(f"  类型: {plan['cardio']['type']}")
    lines.append(f"  时长: {plan['cardio']['duration_min']}分钟/次")
    lines.append(f"  强度: {plan['cardio']['intensity']}")
    hr = plan['cardio']['hr_zone']
    lines.append(f"  心率区间:")
    lines.append(f"    热身: {hr['warmup'][0]}-{hr['warmup'][1]} bpm")
    lines.append(f"    燃脂: {hr['fat_burn'][0]}-{hr['fat_burn'][1]} bpm")
    lines.append(f"    有氧: {hr['cardio'][0]}-{hr['cardio'][1]} bpm")
    lines.append("")

    lines.append(f"💪 力量训练")
    lines.append(f"  频率: {plan['strength']['days_per_week']}次/周")
    lines.append(f"  动作:")
    for ex in plan['strength']['exercises']:
        lines.append(f"    · {ex}")
    lines.append("")

    lines.append(f"📅 一周安排建议")

    week = []
    d = 0
    for _ in range(plan['cardio']['days_per_week']):
        week.append(("有氧", plan['cardio']['type']))
        d += 1
    for _ in range(plan['strength']['days_per_week']):
        week.append(("力量", "力量训练"))
        d += 1
    while d < 7:
        week.append(("休息", "恢复"))
        d += 1

    day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for i, (kind, detail) in enumerate(week):
        lines.append(f"  {day_names[i]}: {kind} → {detail}")

    lines.append("")
    lines.append(f"⏳ 12周渐进计划")

    weeks_progression = {
        1: "适应期：强度60%，动作数量减少1组",
        4: "提升期：强度80%，增加1组",
        8: "强化期：强度90%，增加动作难度",
        12: "维持期：达到目标，转为维持模式",
    }
    for week_num, desc in weeks_progression.items():
        lines.append(f"  第{week_num}周: {desc}")

    lines.append("")
    lines.append("⚠ 安全提示")
    if plan['fitness_level'] == "初级":
        lines.append("  · 初始阶段关注动作标准，而非重量/次数")
        lines.append("  · 每训练4周休息1周，防止过度疲劳")
        lines.append("  · 如有不适立即停止，必要时就医")
        lines.append(f"  · 最大目标心率: {plan['cardio']['hr_max_target']} bpm，不超过此值")
    elif plan['fitness_level'] == "中级":
        lines.append("  · 注意渐进式增加负荷，每周增幅≤10%")
        lines.append("  · 关注关节状态，避免过度训练")
    else:
        lines.append("  · 注意训练与恢复的平衡")
        lines.append("  · 周期性调整训练计划，避免平台期")

    lines.append("")
    lines.append("=" * 55)

    return "\n".join(lines)


# ============================================================
# 入口
# ============================================================

DEFAULT_USER = {
    "gender": "M",
    "age": 35,
    "weight_kg": 85,
    "height_cm": 175,
    "goal": "weight_loss",
    "exercise_frequency": 1,
    "experience": "beginner",
}


def main():
    user = DEFAULT_USER
    bmi = user["weight_kg"] / ((user["height_cm"] / 100) ** 2)

    fitness_level = assess_fitness_level(
        bmi, user["age"], user["exercise_frequency"], user["experience"]
    )

    plan = generate_exercise_plan(user, fitness_level)
    print(format_exercise_plan(plan, user))


if __name__ == "__main__":
    main()
