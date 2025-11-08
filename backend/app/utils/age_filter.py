"""
年龄筛选工具函数
通过直接操作Vue组件实例来设置年龄滑块
"""

import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def set_age_filter_via_vue(frame, min_age: int, max_age: Optional[int] = None) -> dict:
    """
    通过Vue组件直接设置年龄筛选

    Args:
        frame: Playwright的iframe对象（recommendFrame）
        min_age: 最小年龄 (16-60)
        max_age: 最大年龄 (16-60)，None表示不限

    Returns:
        {
            "success": bool,
            "method": "vue2" | "vue3" | None,
            "logs": list,
            "final_values": {"min": str, "max": str},
            "error": str (if failed)
        }

    Example:
        >>> result = await set_age_filter_via_vue(frame, 25, 40)
        >>> print(f"Success: {result['success']}")
        >>> print(f"Age: {result['final_values']['min']}-{result['final_values']['max']}")
    """
    logger.info(f"设置年龄筛选: {min_age} - {max_age if max_age else '不限'}")

    # 验证参数
    if not (16 <= min_age <= 60):
        return {
            "success": False,
            "error": f"最小年龄必须在16-60之间，当前值: {min_age}"
        }

    if max_age is not None and not (16 <= max_age <= 60):
        return {
            "success": False,
            "error": f"最大年龄必须在16-60之间，当前值: {max_age}"
        }

    if max_age is not None and max_age < min_age:
        return {
            "success": False,
            "error": f"最大年龄 ({max_age}) 不能小于最小年龄 ({min_age})"
        }

    # 转换None为60（表示不限）
    max_age_value = max_age if max_age is not None else 60

    try:
        # 调用Vue组件设置年龄
        result = await frame.evaluate("""
        (params) => {
            const slider = document.querySelector('.filter-item.age .vue-slider');
            const logs = [];

            if (!slider) {
                return { success: false, error: '未找到年龄滑块', logs };
            }

            try {
                // Vue 2
                if (slider.__vue__) {
                    logs.push('找到Vue2实例');

                    const component = slider.__vue__;

                    // 方式1: 直接设置value
                    if (component.value !== undefined) {
                        logs.push('设置value属性');
                        component.value = [params.min, params.max];
                    }

                    // 方式2: 调用setValue方法
                    if (typeof component.setValue === 'function') {
                        logs.push('调用setValue方法');
                        component.setValue([params.min, params.max]);
                    }

                    // 方式3: 触发事件
                    if (component.$emit) {
                        logs.push('触发input和change事件');
                        component.$emit('input', [params.min, params.max]);
                        component.$emit('change', [params.min, params.max]);
                    }

                    return { success: true, method: 'vue2', logs };
                }

                // Vue 3
                if (slider.__vueParentComponent) {
                    logs.push('找到Vue3实例');
                    const component = slider.__vueParentComponent;

                    if (component.emit) {
                        logs.push('触发update:modelValue事件');
                        component.emit('update:modelValue', [params.min, params.max]);
                    }

                    return { success: true, method: 'vue3', logs };
                }

                logs.push('未找到Vue实例');
                return { success: false, error: '未找到Vue实例', logs };

            } catch (error) {
                logs.push('错误: ' + error.message);
                return { success: false, error: error.message, logs };
            }
        }
        """, {'min': min_age, 'max': max_age_value})

        # 等待Vue更新
        await asyncio.sleep(0.5)

        # 读取最终值验证
        final_values = await frame.evaluate("""
        () => {
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) return null;

            const tooltips = ageSection.querySelectorAll('.vue-slider-dot-tooltip-text');
            if (tooltips.length >= 2) {
                return {
                    min: tooltips[0].textContent.trim(),
                    max: tooltips[1].textContent.trim()
                };
            }
            return null;
        }
        """)

        result['final_values'] = final_values

        if result['success'] and final_values:
            logger.info(
                f"✅ 年龄设置成功: {final_values['min']} - {final_values['max']}"
            )
        else:
            logger.warning(f"⚠️ 年龄设置可能未生效")

        return result

    except Exception as e:
        logger.error(f"❌ 设置年龄失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "logs": []
        }


async def read_current_age_filter(frame) -> Optional[dict]:
    """
    读取当前的年龄筛选值

    Args:
        frame: Playwright的iframe对象（recommendFrame）

    Returns:
        {"min": str, "max": str} 或 None

    Example:
        >>> age = await read_current_age_filter(frame)
        >>> print(f"当前年龄: {age['min']} - {age['max']}")
    """
    try:
        values = await frame.evaluate("""
        () => {
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) return null;

            const tooltips = ageSection.querySelectorAll('.vue-slider-dot-tooltip-text');
            if (tooltips.length >= 2) {
                return {
                    min: tooltips[0].textContent.trim(),
                    max: tooltips[1].textContent.trim()
                };
            }
            return null;
        }
        """)

        return values

    except Exception as e:
        logger.error(f"读取年龄筛选失败: {str(e)}")
        return None


async def reset_age_filter(frame) -> dict:
    """
    重置年龄筛选为默认值 (22 - 40)

    Args:
        frame: Playwright的iframe对象（recommendFrame）

    Returns:
        操作结果字典

    Example:
        >>> result = await reset_age_filter(frame)
        >>> print(f"Reset success: {result['success']}")
    """
    return await set_age_filter_via_vue(frame, 22, 40)
