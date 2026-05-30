"""canvas-progressive-guard — 视频画布逐节点推进的硬约束（harness 钩子）。

问题背景
========
video-canvas-director SKILL 要求 Hermes "一次只建一个资产节点、跑出来给用户
看、确认后再建下一个"。但 LLM（尤其拿到完整剧本时）倾向于一次性把整条流水线
全规划全建出来，纯靠 SKILL 提示词反复劝不住。

本插件用 Hermes 的 ``pre_tool_call`` harness 钩子做**物理拦截**：

  当 Hermes 调 ``canvas_add_node`` 想加一个【生成型】节点时，先查这个项目的
  画布快照。如果画布上已经存在一个【生成型节点还没跑出产物】（status 既不是
  done 也不是 error，且 outputs 为空），就 block 掉这次 add_node，返回一条
  提示，逼模型先 ``canvas_run_node`` 把上一个跑出来、贴给用户、等用户确认，
  再加下一个。

这样无论模型多想批量铺，第二个未跑节点会被 harness 直接挡回，强制"一个一个来"。

设计要点
========
- 只拦【生成型】节点（image / image2video / inpaint / upscale / tts /
  musicGen / videoConcat / videoExtend / audio2video / comicSplit /
  subtitleRemoval / shotGroup）。``text`` 节点（纯 prompt 容器、不消耗配额、
  不产图）放行 —— 它们常被用作角色 brief / 镜头描述的载体，不该卡。
- "上一个还没跑"的判定基于画布快照里**该项目的真实节点状态**，不是猜。
- 钩子失败一律放行（fail-open）：查不到画布 / 网络错 / 解析错 → 不拦，避免
  把正常使用卡死。安全性靠"宁可漏拦也不错拦"。
- 仅作用于 desktop bridge 的 canvas MCP 工具（tool_name 以 canvas_add_node
  结尾）；其它工具一律不碰。
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 生成型节点：会真正产图/产视频/产音频、消耗配额、需要逐个确认的节点。
_GENERATIVE_KINDS = {
    "image",
    "image2video",
    "inpaint",
    "upscale",
    "tts",
    "musicGen",
    "videoConcat",
    "videoExtend",
    "audio2video",
    "comicSplit",
    "subtitleRemoval",
    "shotGroup",
}

# 这些 kind 不拦：text 是纯 prompt 容器；preview / scriptGen 不产可确认资产。
_FREE_KINDS = {"text", "preview", "scriptGen"}


def _bridge_url() -> str:
    return (
        os.environ.get("HERMES_DESKTOP_BRIDGE_URL")
        or os.environ.get("WORKFLOWX_DESKTOP_BRIDGE_URL")
        or "http://127.0.0.1:8651"
    )


def _node_has_output(node_data: Dict[str, Any]) -> bool:
    """节点是否已经跑出了产物（images/imageUrl/videoUrl/audioUrl 任一非空）。"""
    outputs = node_data.get("outputs")
    if not isinstance(outputs, dict):
        return False
    for v in outputs.values():
        if isinstance(v, list) and len(v) > 0:
            return True
        if isinstance(v, str) and v.strip():
            return True
    return False


def _count_pending_generative_nodes(project_id: str) -> Optional[int]:
    """查画布快照，数"已添加但还没跑出产物"的生成型节点个数。

    返回 None 表示查不到 / 出错（调用方应 fail-open 放行）。
    """
    try:
        import requests  # 延迟导入，避免插件加载期硬依赖
    except Exception:
        return None

    url = f"{_bridge_url()}/canvas/open"
    try:
        resp = requests.post(url, json={"project_id": project_id}, timeout=15)
        if resp.status_code != 200:
            return None
        snapshot = resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.debug("canvas-progressive-guard: open canvas failed: %s", exc)
        return None

    nodes = snapshot.get("nodes")
    if not isinstance(nodes, list):
        return None

    pending = 0
    for node in nodes:
        if not isinstance(node, dict):
            continue
        data = node.get("data")
        if not isinstance(data, dict):
            continue
        kind = data.get("kind")
        if kind not in _GENERATIVE_KINDS:
            continue
        status = str(data.get("status") or "").lower()
        # 已完成 / 失败的节点不算 pending（用户已经能看到结果或错误）。
        if status in {"done", "error"}:
            continue
        # 已经有产物的也不算（即使 status 字段没更新）。
        if _node_has_output(data):
            continue
        pending += 1
    return pending


def _on_pre_tool_call(
    tool_name: str = "",
    args: Optional[Dict[str, Any]] = None,
    task_id: str = "",
    session_id: str = "",
    tool_call_id: str = "",
    **_: Any,
) -> Optional[Dict[str, Any]]:
    """拦截 canvas_add_node：上一个生成节点没跑完就 block。"""
    # 只认 desktop bridge 的 add_node 工具（namespaced: mcp_hermes_desktop_canvas_add_node）。
    if not tool_name.endswith("canvas_add_node"):
        return None
    if not isinstance(args, dict):
        return None

    # data_json 里带 kind；也兼容直接 kind 字段。
    kind = args.get("kind")
    if not kind:
        data_json = args.get("data_json")
        if isinstance(data_json, str) and data_json.strip():
            try:
                import json

                parsed = json.loads(data_json)
                if isinstance(parsed, dict):
                    kind = parsed.get("kind")
            except Exception:
                kind = None

    # 非生成型节点（text / preview / scriptGen）放行。
    if kind in _FREE_KINDS:
        return None
    # kind 解析不出来时保守放行（不误伤）。
    if kind is not None and kind not in _GENERATIVE_KINDS:
        return None

    project_id = args.get("project_id")
    if not isinstance(project_id, str) or not project_id.strip():
        return None  # 没 project_id 无从判断，放行

    pending = _count_pending_generative_nodes(project_id)
    if pending is None:
        return None  # 查不到 → fail-open 放行
    if pending <= 0:
        return None  # 没有未跑节点 → 允许加新节点

    # 有未跑完的生成节点 → 拦截。
    return {
        "action": "block",
        "message": (
            "🚧 逐节点推进守卫：画布上还有 {n} 个【已添加但还没跑出产物】的生成节点。"
            "按视频画布工作流，必须一个资产一个资产做：\n"
            "1. 先用 canvas_run_node 把上一个节点跑出来（mode=\"only\"）；\n"
            "2. 把返回的 displayMarkdown 贴进对话给用户看；\n"
            "3. 问用户满意吗 / 要不要存素材库；\n"
            "4. 用户确认后，再 canvas_add_node 加下一个节点。\n"
            "不要一次性把多个节点全建出来 —— 现在请先跑掉未完成的那个，再继续。"
        ).format(n=pending),
    }


def register(ctx) -> None:
    ctx.register_hook("pre_tool_call", _on_pre_tool_call)
