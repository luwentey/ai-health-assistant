# AI Health Assistant — 示例数据格式

> 所有脚本使用结构化输入，支持 JSON 格式和交互式输入

---

## 1. 用户健康数据 (JSON 格式)

```json
{
  "user": {
    "gender": "M",
    "age": 35,
    "height_cm": 175,
    "weight_kg": 85
  },
  "body_composition": {
    "body_fat_pct": 28.0,
    "muscle_mass_kg": null
  },
  "blood_test": {
    "total_cholesterol": 5.8,
    "hdl": 1.2,
    "ldl": 3.6,
    "triglycerides": 2.1,
    "fasting_glucose": 5.6
  },
  "lifestyle": {
    "activity_level": "sedentary",
    "sleep_hours": 6.5,
    "stress_level": "moderate"
  },
  "goals": {
    "primary": "weight_loss",
    "target_weight_kg": 72,
    "deadline_weeks": 12
  },
  "dietary_preferences": {
    "allergies": ["seafood"],
    "avoid": ["pork"],
    "meals_per_day": 3
  },
  "exercise_history": {
    "frequency_per_week": 1,
    "type": "running",
    "experience": "beginner"
  }
}
```

## 2. 示例输出

### 健康报告摘要

```
═══════════════════════════════════════════
  AI 健康分析报告
═══════════════════════════════════════════

📋 个人信息
  年龄: 35岁 | 性别: 男 | 身高: 175cm | 体重: 85kg

📊 关键指标
  BMI: 27.8 (超重 ⚠) | 标准: 18.5-24
  体脂率: 28.0% (肥胖 ⚠) | 标准: 15-20%
  总胆固醇: 5.8mmol/L (偏高 ⚠)

🔴 健康风险
  代谢综合征风险: 中
  心血管风险: 中

📝 改善建议
  [优先级A] 控制体重至72kg，12周计划
  [优先级A] 降低总胆固醇，减少饱和脂肪摄入
  [优先级B] 增加有氧运动，每周≥150分钟
```

### 饮食方案摘要

```
═══════════════════════════════════════════
  AI 饮食规划方案
═══════════════════════════════════════════

🎯 热量目标: 1420 kcal/日

🥣 早餐 (430 kcal)
  全麦面包 2片 + 鸡蛋 2个 + 牛奶 250ml

🥗 午餐 (500 kcal)
  鸡胸肉 150g + 糙米饭 100g + 蔬菜 200g

🥘 晚餐 (350 kcal)
  三文鱼 120g + 西兰花 150g + 玉米 80g

🍎 加餐 (140 kcal)
  苹果 1个 + 坚果 15g

⚠ 禁忌提醒: 海鲜过敏，避免含海鲜成分的调味品
```

### 运动方案摘要

```
═══════════════════════════════════════════
  AI 运动推荐方案
═══════════════════════════════════════════

🎯 目标: 12周减脂增肌

🏃 有氧训练
  周一/三/五: 快走 40min (心率 120-140)
  周六: 游泳 30min

💪 力量训练（周二/四）
  深蹲 3×12 → 俯卧撑 3×10 → 划船 3×12
  平板支撑 3×30s

⚠ 安全提示
  初始阶段避免高强度训练
  关注膝盖状态，如有不适立即停止
```
