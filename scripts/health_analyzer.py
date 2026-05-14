#!/usr/bin/env python3
"""
AI Health Analyzer — AI 健康分析引擎

模拟大模型对健康数据的推理分析过程，展示：
1. 多指标交叉分析（BMI + 体脂 + 血脂）
2. 异常检测与风险分级
3. 个体化改善建议生成

使用方式：
    python health_analyzer.py [--interactive]
"""

import sys
import json
import math


# ============================================================
# 标准知识库
# ============================================================

BMI_STANDARDS = [
    (0, 18.5, "偏瘦", "info"),
    (18.5, 24, "正常", "pass"),
    (24, 28, "超重", "warn"),
    (28, 100, "肥胖", "danger"),
]

BODY_FAT_STANDARDS = {
    "M": [(0, 15, "偏低"), (15, 20, "正常"), (20, 25, "偏高"), (25, 100, "肥胖")],
    "F": [(0, 20, "偏低"), (20, 25, "正常"), (25, 30, "偏高"), (30, 100, "肥胖")],
}

CHOLESTEROL_THRESHOLDS = {
    "total_cholesterol": (5.2, 6.2, "总胆固醇"),
    "hdl": (1.0, 1.55, "高密度脂蛋白"),
    "ldl": (3.4, 4.1, "低密度脂蛋白"),
    "triglycerides": (1.7, 2.3, "甘油三酯"),
    "fasting_glucose": (6.1, 7.0, "空腹血糖"),
}


def classify_bmi(bmi):
    for low, high, label, level in BMI_STANDARDS:
        if low <= bmi < high:
            return label, level
    return "异常", "danger"


def classify_body_fat(pct, gender):
    standards = BODY_FAT_STANDARDS.get(gender, BODY_FAT_STANDARDS["M"])
    for low, high, label in standards:
        if low <= pct < high:
            return label
    return "异常"


def calc_bmr(weight_kg, height_cm, age, gender):
    """Mifflin-St Jeor 基础代谢率公式"""
    if gender == "M":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calc_bmi(weight_kg, height_cm):
    return weight_kg / ((height_cm / 100) ** 2)


# ============================================================
# 风险评估
# ============================================================

def assess_metabolic_risk(data):
    """
    代谢综合征风险评估（ATP III 标准）

    评估项：
    1. 腰围（用BMI代替估算）
    2. 甘油三酯 ≥ 1.7
    3. HDL < 1.0(男) / 1.3(女)
    4. 血压 ≥ 130/85（用BMI估算）
    5. 空腹血糖 ≥ 6.1
    """
    risk_items = 0

    bmi = calc_bmi(data["weight_kg"], data["height_cm"])
    if bmi >= 28:
        risk_items += 1  # 腰围超标估计

    tg = data.get("blood_test", {}).get("triglycerides", 0)
    if tg >= 1.7:
        risk_items += 1

    hdl = data.get("blood_test", {}).get("hdl", 0)
    gender = data.get("gender", "M")
    if (gender == "M" and hdl < 1.0) or (gender == "F" and hdl < 1.3):
        risk_items += 1

    if bmi >= 24:
        risk_items += 1  # 用BMI估算血压

    glucose = data.get("blood_test", {}).get("fasting_glucose", 0)
    if glucose >= 6.1:
        risk_items += 1

    if risk_items >= 3:
        return "高（≥3项异常）"
    elif risk_items >= 2:
        return "中（2项异常）"
    else:
        return "低"


def assess_cardiovascular_risk(data):
    """简化版心血管风险评估"""
    score = 0
    bmi = calc_bmi(data["weight_kg"], data["height_cm"])
    age = data.get("age", 0)

    # 年龄
    if age > 45:
        score += 1

    # BMI
    if bmi >= 28:
        score += 2
    elif bmi >= 24:
        score += 1

    # 胆固醇
    tc = data.get("blood_test", {}).get("total_cholesterol", 0)
    if tc > 6.2:
        score += 2
    elif tc > 5.2:
        score += 1

    # 血糖
    glucose = data.get("blood_test", {}).get("fasting_glucose", 0)
    if glucose > 7.0:
        score += 2
    elif glucose > 6.1:
        score += 1

    # 生活方式
    lifestyle = data.get("lifestyle", {})
    if lifestyle.get("activity_level") == "sedentary":
        score += 1

    if score >= 5:
        return "高"
    elif score >= 3:
        return "中"
    else:
        return "低"


# ============================================================
# 报告生成
# ============================================================

WARN_ICON = {"pass": "✓", "warn": "⚠", "danger": "✗", "info": "ℹ"}


def generate_report(data):
    """综合健康分析报告生成"""
    gender = data.get("gender", "M")
    age = data.get("age", 30)
    weight = data.get("weight_kg", 70)
    height = data.get("height_cm", 170)
    body_fat = data.get("body_composition", {}).get("body_fat_pct", None)

    # 基础计算
    bmi = calc_bmi(weight, height)
    bmr = calc_bmr(weight, height, age, gender)
    bmi_label, bmi_level = classify_bmi(bmi)

    # 报告构建
    lines = []
    lines.append("=" * 55)
    lines.append("  AI 健康分析报告")
    lines.append("=" * 55)
    lines.append("")

    # 个人信息
    gender_cn = "男" if gender == "M" else "女"
    lines.append(f"📋 个人信息")
    lines.append(f"  {age}岁 | {gender_cn} | {height}cm | {weight}kg")
    lines.append("")

    # 关键指标
    lines.append("📊 关键指标")

    icon = WARN_ICON.get(bmi_level, "ℹ")
    lines.append(f"  BMI: {bmi:.1f} ({bmi_label}) {icon}  | 标准: 18.5-24")

    if body_fat:
        fat_label = classify_body_fat(body_fat, gender)
        fat_icon = "⚠" if fat_label in ("偏高", "肥胖") else "✓"
        fat_std = "15-20%" if gender == "M" else "20-25%"
        lines.append(f"  体脂率: {body_fat:.1f}% ({fat_label}) {fat_icon} | 标准: {fat_std}")

    # 血检指标
    blood = data.get("blood_test", {})
    if blood:
        for key, (warn_thresh, danger_thresh, label) in CHOLESTEROL_THRESHOLDS.items():
            val = blood.get(key)
            if val is not None:
                if val >= danger_thresh:
                    icon = "✗"
                    status = "偏高(需就医)" if key != "hdl" else "偏低(需就医)"
                elif val >= warn_thresh:
                    icon = "⚠"
                    status = "偏高" if key != "hdl" else "偏低"
                else:
                    icon = "✓"
                    status = "正常"

                if key == "hdl":
                    icon = "✗" if val < warn_thresh else ("⚠" if val < danger_thresh else "✓")
                    status = "偏低" if val < warn_thresh else "正常"

                lines.append(f"  {label}: {val}mmol/L ({status}) {icon}")

    lines.append("")

    # 基础代谢
    lines.append(f"🔥 基础代谢: {bmr:.0f} kcal/日")
    lines.append("")

    # 风险评估
    lines.append("🔴 健康风险评估")
    mr = assess_metabolic_risk(data)
    cv = assess_cardiovascular_risk(data)

    mr_icon = "✗" if mr.startswith("高") else ("⚠" if mr.startswith("中") else "✓")
    cv_icon = "✗" if cv == "高" else ("⚠" if cv == "中" else "✓")

    lines.append(f"  代谢综合征风险: {mr} {mr_icon}")
    lines.append(f"  心血管风险: {cv} {cv_icon}")
    lines.append("")

    # 改善建议
    lines.append("📝 改善建议")

    # 基于分析结果生成建议
    priorities = []

    if bmi >= 24:
        target_bmi = 22
        target_weight = target_bmi * ((height / 100) ** 2)
        loss_weeks = 12
        deficit_per_day = ((weight - target_weight) * 7700) / (loss_weeks * 7)
        priorities.append((
            "A",
            f"控制体重",
            f"目标 {target_weight:.0f}kg（BMI={target_bmi:.1f}），{loss_weeks}周计划，每日缺口{deficit_per_day:.0f}kcal"
        ))

    tc = blood.get("total_cholesterol", 0)
    if tc > 5.2:
        priorities.append(("A", "降低总胆固醇", "减少饱和脂肪摄入，增加膳食纤维"))

    if lifestyle.get("activity_level") == "sedentary":
        priorities.append(("B", "增加运动", "每周≥150分钟中等强度有氧运动"))

    if lifestyle.get("sleep_hours", 8) < 7:
        priorities.append(("B", "改善睡眠", "目标7-8小时/日"))

    for priority, title, detail in priorities:
        lines.append(f"  [优先级{priority}] {title}")
        lines.append(f"    {detail}")

    lines.append("")
    lines.append("=" * 55)

    return "\n".join(lines)


# ============================================================
# 默认示例
# ============================================================

DEFAULT_DATA = {
    "gender": "M",
    "age": 35,
    "height_cm": 175,
    "weight_kg": 85,
    "body_composition": {"body_fat_pct": 28.0},
    "blood_test": {
        "total_cholesterol": 5.8,
        "hdl": 1.2,
        "ldl": 3.6,
        "triglycerides": 2.1,
        "fasting_glucose": 5.6,
    },
    "lifestyle": {
        "activity_level": "sedentary",
        "sleep_hours": 6.5,
        "stress_level": "moderate",
    },
}


def interactive_mode():
    """交互式输入模式"""
    data = {**DEFAULT_DATA}

    print("\n=== 健康数据输入 ===")
    gender = input("性别 (M/F) [M]: ").strip().upper() or "M"
    data["gender"] = gender

    age = input("年龄 [35]: ").strip()
    data["age"] = int(age) if age else 35

    height = input("身高(cm) [175]: ").strip()
    data["height_cm"] = float(height) if height else 175

    weight = input("体重(kg) [85]: ").strip()
    data["weight_kg"] = float(weight) if weight else 85

    bf = input("体脂率(%)(可选): ").strip()
    if bf:
        data["body_composition"] = {"body_fat_pct": float(bf)}

    print("\n" + generate_report(data))


def main():
    if "--interactive" in sys.argv:
        interactive_mode()
    else:
        print(generate_report(DEFAULT_DATA))


if __name__ == "__main__":
    main()
