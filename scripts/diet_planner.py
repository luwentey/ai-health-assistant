#!/usr/bin/env python3
"""
AI Diet Planner — AI 饮食营养规划

模拟大模型对饮食营养的推理分析，展示：
1. 个体化热量需求计算
2. 宏量营养素分配优化
3. 智能食谱生成与禁忌筛查

使用方式：
    python diet_planner.py
"""

import math


# ============================================================
# 常量知识库
# ============================================================

# 活动系数
ACTIVITY_FACTOR = {
    "sedentary": 1.2,  # 久坐
    "light": 1.375,  # 轻度活动
    "moderate": 1.55,  # 中度活动
    "active": 1.725,  # 活跃
    "very_active": 1.9,  # 高强度
}

# 目标调整系数
GOAL_ADJUSTMENT = {
    "weight_loss_fast": 0.75,  # 快速减脂
    "weight_loss": 0.80,  # 减脂
    "weight_loss_slow": 0.85,  # 缓慢减脂
    "maintain": 1.0,  # 维持
    "muscle_gain_slow": 1.1,  # 缓慢增肌
    "muscle_gain": 1.15,  # 增肌
    "muscle_gain_fast": 1.2,  # 快速增肌
}

# 宏量营养素比例 (基于目标)
MACRO_RATIOS = {
    "weight_loss": {"protein": 0.35, "fat": 0.25, "carbs": 0.40},
    "maintain": {"protein": 0.25, "fat": 0.25, "carbs": 0.50},
    "muscle_gain": {"protein": 0.30, "fat": 0.20, "carbs": 0.50},
}

# 食物数据库（简化版）
FOOD_DB = {
    "蛋白质": [
        {"name": "鸡胸肉", "per_100g": {"kcal": 133, "protein": 31, "fat": 1.2, "carbs": 0}},
        {"name": "鸡蛋(个)", "per_100g": {"kcal": 144, "protein": 13.3, "fat": 8.8, "carbs": 1.6}, "unit_size": 50},
        {"name": "牛奶(250ml)", "per_100ml": {"kcal": 67, "protein": 3.3, "fat": 3.8, "carbs": 4.8}, "unit_size": 250},
        {"name": "三文鱼", "per_100g": {"kcal": 208, "protein": 20.4, "fat": 13.4, "carbs": 0}},
        {"name": "豆腐", "per_100g": {"kcal": 76, "protein": 8.1, "fat": 3.7, "carbs": 2.8}},
        {"name": "牛肉(瘦)", "per_100g": {"kcal": 125, "protein": 21.3, "fat": 3.8, "carbs": 0.4}},
    ],
    "碳水": [
        {"name": "糙米饭", "per_100g": {"kcal": 111, "protein": 2.6, "fat": 0.9, "carbs": 23.0}},
        {"name": "全麦面包(片)", "per_100g": {"kcal": 246, "protein": 8.5, "fat": 3.4, "carbs": 41.0}, "unit_size": 40},
        {"name": "红薯", "per_100g": {"kcal": 86, "protein": 1.6, "fat": 0.1, "carbs": 20.0}},
        {"name": "燕麦", "per_100g": {"kcal": 367, "protein": 13.5, "fat": 6.7, "carbs": 60.0}},
        {"name": "玉米", "per_100g": {"kcal": 96, "protein": 3.3, "fat": 1.2, "carbs": 19.0}},
        {"name": "意面(干)", "per_100g": {"kcal": 350, "protein": 12.0, "fat": 1.5, "carbs": 73.0}},
    ],
    "脂肪": [
        {"name": "橄榄油", "per_100g": {"kcal": 884, "protein": 0, "fat": 100, "carbs": 0}},
        {"name": "坚果", "per_100g": {"kcal": 553, "protein": 20, "fat": 49, "carbs": 16}},
        {"name": "牛油果", "per_100g": {"kcal": 160, "protein": 2, "fat": 15, "carbs": 8}},
    ],
    "蔬菜": [
        {"name": "西兰花", "per_100g": {"kcal": 34, "protein": 2.8, "fat": 0.4, "carbs": 6.6}},
        {"name": "菠菜", "per_100g": {"kcal": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6}},
        {"name": "番茄", "per_100g": {"kcal": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9}},
        {"name": "黄瓜", "per_100g": {"kcal": 15, "protein": 0.8, "fat": 0.1, "carbs": 2.9}},
        {"name": "生菜", "per_100g": {"kcal": 15, "protein": 1.4, "fat": 0.2, "carbs": 2.9}},
    ],
    "水果": [
        {"name": "苹果", "per_100g": {"kcal": 52, "protein": 0.3, "fat": 0.2, "carbs": 14.0}, "unit_size": 200},
        {"name": "香蕉", "per_100g": {"kcal": 89, "protein": 1.1, "fat": 0.3, "carbs": 20.0}, "unit_size": 120},
        {"name": "蓝莓", "per_100g": {"kcal": 57, "protein": 0.7, "fat": 0.3, "carbs": 14.5}},
    ],
}


# ============================================================
# 核心计算
# ============================================================

def calc_bmr(weight_kg, height_cm, age, gender="M"):
    """Mifflin-St Jeor 公式"""
    if gender == "M":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_calories(bmr, activity_level, goal, weight_kg):
    """计算目标热量"""
    factor = ACTIVITY_FACTOR.get(activity_level, 1.2)
    maintain = bmr * factor
    goal_factor = GOAL_ADJUSTMENT.get(goal, 1.0)

    if goal.startswith("weight_loss"):
        target = maintain * goal_factor
        protein_factor = 1.8  # g/kg 体重
    elif goal.startswith("muscle_gain"):
        target = maintain * goal_factor
        protein_factor = 1.6
    else:
        target = maintain
        protein_factor = 1.2

    protein_g = weight_kg * protein_factor
    protein_kcal = protein_g * 4

    return target, protein_g, protein_kcal


def generate_meal_plan(target_kcal, protein_g, goal, weight_kg, allergies=None):
    """生成一日饮食方案"""
    allergies = allergies or []

    ratios = MACRO_RATIOS.get("weight_loss" if goal.startswith("weight_loss")
                              else ("muscle_gain" if goal.startswith("muscle_gain") else "maintain"), {})

    target_protein_kcal = target_kcal * ratios.get("protein", 0.25)
    target_fat_kcal = target_kcal * ratios.get("fat", 0.25)
    target_carbs_kcal = target_kcal * ratios.get("carbs", 0.50)

    target_protein_g = target_protein_kcal / 4
    target_fat_g = target_fat_kcal / 9
    target_carbs_g = target_carbs_kcal / 4

    # 三餐分配比率
    meal_split = {"breakfast": 0.3, "lunch": 0.35, "dinner": 0.25, "snack": 0.1}

    # 生成食谱（基于简化逻辑）
    def pick_food(category, kcal_target, exclude=None):
        exclude = exclude or []
        foods = [f for f in FOOD_DB.get(category, []) if f["name"] not in exclude]
        if not foods:
            return []
        result = []
        for food in foods:
            if any(a in food["name"] for a in allergies):
                continue
            unit = food.get("unit_size", 100)
            per_unit_kcal = None
            if "per_100g" in food:
                per_unit_kcal = food["per_100g"]["kcal"] * unit / 100
            elif "per_100ml" in food:
                per_unit_kcal = food["per_100ml"]["kcal"] * unit / 100

            if per_unit_kcal and per_unit_kcal <= kcal_target + 50:
                result.append((food["name"], per_unit_kcal, unit))
        return result[:1]

    meal_plan = []

    # 早餐
    bf_kcal = target_kcal * meal_split["breakfast"]
    bf_items = []
    bf_items.append(f"全麦面包 2片 ({84}g) ≈ {int(FOOD_DB['碳水'][1]['per_100g']['kcal']*0.84)}kcal")
    bf_items.append(f"鸡蛋 2个 ≈ {int(FOOD_DB['蛋白质'][1]['per_100g']['kcal']*1)}kcal")
    bf_items.append(f"牛奶 250ml ≈ {int(FOOD_DB['蛋白质'][2]['per_100ml']['kcal']*2.5)}kcal")
    meal_plan.append(("🥣 早餐", bf_items, int(bf_kcal)))

    # 午餐
    lunch_kcal = target_kcal * meal_split["lunch"]
    lunch_items = []
    lunch_items.append(f"鸡胸肉 150g ≈ {int(FOOD_DB['蛋白质'][0]['per_100g']['kcal']*1.5)}kcal")
    lunch_items.append(f"糙米饭 100g ≈ {int(FOOD_DB['碳水'][0]['per_100g']['kcal'])}kcal")
    lunch_items.append(f"西兰花 200g ≈ {int(FOOD_DB['蔬菜'][0]['per_100g']['kcal']*2)}kcal")
    meal_plan.append(("🥗 午餐", lunch_items, int(lunch_kcal)))

    # 晚餐
    dinner_kcal = target_kcal * meal_split["dinner"]
    dinner_items = []
    dinner_items.append(f"三文鱼 120g ≈ {int(FOOD_DB['蛋白质'][3]['per_100g']['kcal']*1.2)}kcal")
    dinner_items.append(f"蔬菜沙拉 150g ≈ {int(FOOD_DB['蔬菜'][3]['per_100g']['kcal']*1.5)}kcal")
    dinner_items.append(f"红薯 80g ≈ {int(FOOD_DB['碳水'][2]['per_100g']['kcal']*0.8)}kcal")
    meal_plan.append(("🥘 晚餐", dinner_items, int(dinner_kcal)))

    # 加餐
    snack_kcal = target_kcal * meal_split["snack"]
    snack_items = []
    snack_items.append(f"苹果 1个 ≈ {int(FOOD_DB['水果'][0]['per_100g']['kcal']*2)}kcal")
    snack_items.append(f"坚果 15g ≈ {int(FOOD_DB['脂肪'][1]['per_100g']['kcal']*0.15)}kcal")
    meal_plan.append(("🍎 加餐", snack_items, int(snack_kcal)))

    return meal_plan, {
        "total_kcal": target_kcal,
        "protein": target_protein_g,
        "fat": target_fat_g,
        "carbs": target_carbs_g,
    }


def format_meal_plan(meal_plan, nutrition, user_data):
    """格式化输出饮食方案"""
    lines = []
    lines.append("=" * 55)
    lines.append("  AI 饮食规划方案")
    lines.append("=" * 55)
    lines.append("")

    goal_labels = {
        "weight_loss": "减脂",
        "weight_loss_fast": "快速减脂",
        "maintain": "体重维持",
        "muscle_gain": "增肌",
    }
    goal_label = goal_labels.get(user_data.get("goal", "weight_loss"), "减脂")

    lines.append(f"🎯 目标: {goal_label}")
    lines.append(f"🔥 热量目标: {nutrition['total_kcal']:.0f} kcal/日")
    lines.append(f"📊 营养配比: 蛋白质 {nutrition['protein']:.0f}g | "
                 f"脂肪 {nutrition['fat']:.0f}g | 碳水 {nutrition['carbs']:.0f}g")
    lines.append("")

    for meal_name, items, kcal in meal_plan:
        lines.append(f"{meal_name} ({kcal}kcal)")
        for item in items:
            lines.append(f"  {item}")
        lines.append("")

    # 禁忌提醒
    allergies = user_data.get("allergies", [])
    if allergies:
        lines.append("⚠ 禁忌提醒")
        for a in allergies:
            lines.append(f"  · {a}过敏，避免含{0}成分食物")
        lines.append("")

    lines.append("💡 AI 建议")
    lines.append("  · 多喝水，保证2L/日")
    lines.append("  · 饮食配合运动效果更佳")
    if goal_label == "减脂":
        lines.append("  · 控制烹饪用油，避免额外热量")

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
    "activity_level": "sedentary",
    "goal": "weight_loss",
    "allergies": ["seafood"],
}


def main():
    user = DEFAULT_USER

    bmr = calc_bmr(user["weight_kg"], user["height_cm"], user["age"], user["gender"])
    target_kcal, protein_g, protein_kcal = calculate_calories(
        bmr, user["activity_level"], user["goal"], user["weight_kg"]
    )

    meal_plan, nutrition = generate_meal_plan(
        target_kcal, protein_g, user["goal"], user["weight_kg"], user["allergies"]
    )

    print(format_meal_plan(meal_plan, nutrition, user))


if __name__ == "__main__":
    main()
