"""
WorkflowX Desktop Bridge MCP Server.

Exposes desktop-only capabilities (local workflows and browser bridge) to any
Hermes session, including Weixin / Feishu / CLI, through a standard MCP server.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import requests

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Desktop bridge MCP server requires the 'mcp' package."
    ) from exc


BRIDGE_URL = os.environ.get(
    "HERMES_DESKTOP_BRIDGE_URL",
    os.environ.get("WORKFLOWX_DESKTOP_BRIDGE_URL", "http://127.0.0.1:8651"),
)
mcp = FastMCP(
    "hermes_desktop",
    instructions=(
        "Hermes desktop bridge. Use these tools to access local workflows, "
        "knowledge notes, wiki content, and browser-harness capabilities from "
        "any Hermes conversation. "
        "When a user asks about prior notes, local docs, wiki pages, or knowledge-base content, "
        "first use knowledge_search or wiki_lookup to find candidates, then use knowledge_read "
        "to inspect the most relevant notes before answering. "
        "If the current session context includes a session_key, pass it to "
        "workflow_run, browser_setup, and browser_connect so the desktop app "
        "can attach audit records back to the originating conversation."
    ),
)


def _request_json(method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{BRIDGE_URL}{path}"
    try:
        response = requests.request(method, url, params=params, timeout=120)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "url": url,
        }


def _dump(payload: dict[str, Any] | list[Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _clean_params(**kwargs: Any) -> dict[str, Any] | None:
    params = {key: value for key, value in kwargs.items() if value not in (None, "", [])}
    return params or None


def _parse_url_list(value: Any) -> list[str]:
    """Robustly parse a list of URLs from MCP tool args.

    Accepts either a JSON-encoded array string ("[\"url1\",\"url2\"]"),
    a comma-separated string ("url1,url2"), or a real list. LLMs differ in
    how they emit list args, so we accept all three.
    """
    if value is None or value == "" or value == []:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if v and str(v).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        # Try JSON array first
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(v).strip() for v in parsed if v and str(v).strip()]
            except json.JSONDecodeError:
                pass
        # Fall back to comma-separated
        return [u.strip() for u in text.split(",") if u.strip()]
    return [str(value).strip()]


@mcp.tool()
def desktop_health() -> str:
    """Check whether the local WorkflowX desktop bridge is reachable."""
    return _dump(_request_json("GET", "/health"))


@mcp.tool()
def workflows_list() -> str:
    """List local WorkflowX workflows available on this desktop."""
    return _dump(_request_json("GET", "/workflows"))


@mcp.tool()
def workflow_run(workflow_id: str, session_key: str = "") -> str:
    """Execute one local WorkflowX workflow by id.

    Args:
        workflow_id: Workflow id returned by workflows_list().
        session_key: Optional current Hermes session key for audit association.
    """
    params = _clean_params(session_key=session_key)
    return _dump(_request_json("POST", f"/workflows/{workflow_id}/execute", params=params))


@mcp.tool()
def knowledge_search(query: str, limit: int = 6, item_type: str = "") -> str:
    """Search Hermes Desktop knowledge items and vault notes.

    Args:
        query: Natural-language search query.
        limit: Max number of results to return, capped by the desktop bridge.
        item_type: Optional filter such as "wiki" or "note".
    """
    return _dump(
        _request_json(
            "GET",
            "/knowledge/search",
            params=_clean_params(q=query, limit=limit, item_type=item_type),
        )
    )


@mcp.tool()
def knowledge_read(note_id: str) -> str:
    """Read one Hermes Desktop knowledge note by id."""
    return _dump(_request_json("GET", f"/knowledge/notes/{note_id}"))


@mcp.tool()
def knowledge_write_note(
    title: str,
    content: str,
    project: str = "",
    note_id: str = "",
    tags: list | None = None,
    sort_order: int | None = None,
) -> str:
    """把一篇笔记写进 Hermes 知识库（vault），写完立即可被 knowledge_search 检索到。

    给写小说/做笔记沉淀等场景存内容用 —— 例如 novel-writer skill 用它存
    故事圣经、大纲、人物小传、每一章正文。

    Args:
        title: 笔记标题。**建议带项目/书名前缀**便于后续检索，
               如 "我的小说 · 第12章 · 夜袭"、"我的小说 · 人物 · 林尘"、
               "我的小说 · 大纲"、"我的小说 · 故事圣经"。
        content: 笔记正文（markdown）。章节正文开头建议放一行元信息：
               【书名：x | 第N章 | 标题：x | 上一章结尾：x | 本章目标：x】
        project: 归属项目（vault 子目录），写小说时用书名，让同一本书的
               笔记归到一起。空 = 存到 "raw" 根目录。**强烈建议写小说时一定
               传 project=书名**，这样 knowledge_list_notes 才能按书把章节列全。
        note_id: 已有笔记 id（传了 = 覆盖更新那篇，用于改章节/更新大纲；
               不传 = 新建一篇）。
        tags: 标签列表，如 ["书名", "novel", "chapter"]，便于过滤检索。
        sort_order: 排序序号。**写章节时务必传成章节号**（第 N 章 → sort_order=N），
               大纲/故事圣经/人物设定建议用 0 或负数排在最前。这样
               knowledge_list_notes 能按章节顺序确定性返回，续写时稳定取到上一章。

    返回 {"ok": true, "id": "...", "title": "...", "relativePath": "..."}。
    拿到的 id 可用于之后 knowledge_read 精确读回，或再次 knowledge_write_note 覆盖更新。
    """
    body: dict = {"title": title, "content": content}
    if project.strip():
        body["project"] = project.strip()
    if note_id.strip():
        body["id"] = note_id.strip()
    if tags:
        body["tags"] = tags
    if sort_order is not None:
        body["sort_order"] = int(sort_order)
    return _dump(_post_json("/knowledge/write", body, timeout=60))


@mcp.tool()
def knowledge_delete_note(note_id: str) -> str:
    """删除一条知识库笔记，同时清理关联的 wiki 页面和反向链接。

    使用场景：用户说"删除这篇笔记" / "把 X 删掉" → 用这个工具。

    注意：
      - 会删除笔记文件本身
      - 会清理关联的 wiki 页面
      - 会清理其他笔记中指向它的反向链接（[[title]] 格式）
      - 这是不可逆操作，会提示用户确认

    Args:
        note_id: 笔记 ID（来自 knowledge_list_notes 或 knowledge_search）

    返回 {"ok": true} 或 {"ok": false, "error": "..."}
    """
    return _dump(_post_json("/knowledge/delete_note", {"note_id": note_id}, timeout=30))


@mcp.tool()
def knowledge_list_notes(
    project: str,
    item_type: str = "",
    limit: int = 200,
    order: str = "asc",
) -> str:
    """按项目（书名）确定性列出该项目下全部笔记，按 sort_order（章节号）排序。

    **续写小说/查阅整本书结构时用这个，而不是 knowledge_search。**
    knowledge_search 是模糊相关度排序且有 limit 截断，章节一多就可能漏掉
    正确的上一章；本工具按 project 精确过滤、按 sort_order 稳定排序，能
    可靠地拿到「大纲 / 故事圣经 / 第 1..N 章」的完整有序清单。

    典型用法（续写第 N 章前）：
      1. knowledge_list_notes(project="书名") 拿到有序章节清单 + 各自 id
      2. 对大纲、故事圣经、上一章（sort_order=N-1）用 knowledge_read(id) 读全文
      3. 据此续写第 N 章，再用 knowledge_write_note(project="书名", sort_order=N) 存回

    Args:
        project: 项目/书名（写笔记时传的 project）。必填。
        item_type: 可选 item_type 过滤，如 "note"。
        limit: 最大返回条数，默认 200，封顶 500。
        order: "asc"（默认，章节号升序）或 "desc"（倒序，便于拿最新几章）。

    返回 {"project": "...", "count": N, "notes": [{id, title, summary,
    sortOrder, relativePath, tags, updatedAt}, ...]}。summary 是正文前 220 字预览，
    需要全文再用 knowledge_read(id)。
    """
    return _dump(
        _request_json(
            "GET",
            "/knowledge/list_project_notes",
            params=_clean_params(
                project=project,
                item_type=item_type,
                limit=limit,
                order=order,
            ),
        )
    )


@mcp.tool()
def knowledge_resolve(query: str, limit: int = 5, max_reads: int = 3, item_type: str = "") -> str:
    """Search Hermes Desktop knowledge, pick the strongest candidates, and read them.

    Use this when the user asks a question grounded in the local knowledge base and
    you want the relevant source texts in one step.

    Args:
        query: Natural-language question or retrieval query.
        limit: Max number of candidates to inspect from search.
        max_reads: Max number of notes to read after search.
        item_type: Optional filter such as "wiki" or "note".
    """
    search_payload = _request_json(
        "GET",
        "/knowledge/search",
        params=_clean_params(q=query, limit=limit, item_type=item_type),
    )
    if isinstance(search_payload, dict) and not search_payload.get("ok", True):
        return _dump(search_payload)

    candidates = search_payload if isinstance(search_payload, list) else []
    selected = candidates[: max(1, min(max_reads, len(candidates)))]
    notes = []
    for item in selected:
        note_id = item.get("id")
        if not note_id:
            continue
        notes.append(_request_json("GET", f"/knowledge/notes/{note_id}"))

    return _dump(
        {
            "query": query,
            "candidates": candidates,
            "notes": notes,
        }
    )


@mcp.tool()
def wiki_lookup(query: str, limit: int = 4) -> str:
    """Search Hermes Desktop wiki notes when the user asks for local wiki knowledge."""
    return _dump(
        _request_json(
            "GET",
            "/knowledge/search",
            params=_clean_params(q=query, limit=limit, item_type="wiki"),
        )
    )


@mcp.tool()
def wiki_index() -> str:
    """Read the current internal wiki index before drilling into specific pages."""
    return _dump(_request_json("GET", "/wiki/index"))


@mcp.tool()
def wiki_schema() -> str:
    """Read the current internal wiki schema and maintenance protocol."""
    return _dump(_request_json("GET", "/wiki/schema"))


@mcp.tool()
def wiki_log() -> str:
    """Read the recent internal wiki maintenance log."""
    return _dump(_request_json("GET", "/wiki/log"))


@mcp.tool()
def wiki_rebuild() -> str:
    """Rebuild wiki pages from current raw notes on Hermes Desktop."""
    return _dump(_request_json("POST", "/wiki/rebuild"))


@mcp.tool()
def wiki_lint() -> str:
    """Run Hermes Desktop wiki lint and cleanup orphan/system issues."""
    return _dump(_request_json("POST", "/wiki/lint"))


@mcp.tool()
def wiki_record_proposals(proposals_json: str) -> str:
    """Record one or more structured wiki maintenance proposals into Hermes Desktop.

    Args:
        proposals_json: JSON array of proposal objects with action/rationale/evidence fields.
    """
    url = f"{BRIDGE_URL}/wiki/proposals"
    try:
        payload = {"proposals": json.loads(proposals_json)}
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return _dump(response.json())
    except Exception as exc:
        return _dump({
            "ok": False,
            "error": str(exc),
            "url": url,
        })


@mcp.tool()
def wiki_compile_note(note_id: str) -> str:
    """Compile or refresh one raw note into its stable wiki page."""
    return _dump(_request_json("POST", f"/wiki/notes/{note_id}/compile"))


@mcp.tool()
def browser_overview() -> str:
    """Read the current browser-harness status from the desktop app."""
    return _dump(_request_json("GET", "/browser/overview"))


@mcp.tool()
def browser_setup(session_key: str = "") -> str:
    """Prepare the bundled browser-harness environment on the desktop app."""
    params = _clean_params(session_key=session_key)
    return _dump(_request_json("POST", "/browser/setup", params=params))


@mcp.tool()
def browser_connect(session_key: str = "") -> str:
    """Start or re-attach browser-harness so Hermes can drive the local browser."""
    params = _clean_params(session_key=session_key)
    return _dump(_request_json("POST", "/browser/prime", params=params))



# ──────────────── Video Canvas tools (编排式 / Orchestration) ────────────────
#
# 核心理念：hermes 是导演，画布是剧组。
# hermes 不应该直接调 API 生成图/视频，而应该：
#   1. 创建画布项目
#   2. 在画布上添加节点 + 连线，搭出一个完整的可执行 pipeline
#   3. 用户在 UI 看到完整 pipeline 后，手动 / hermes 运行某些节点
#
# 节点类型（kind）：
#   - scriptGen: 故事脚本生成 → 输出分场列表
#   - image: 通用文生图
#   - inpaint: 局部修改
#   - upscale: 高清化
#   - image2video: 图生视频
#   - audio2video: 音频生视频（口型同步）
#   - tts: 文本转语音
#   - videoConcat: 视频拼接成片
#   - videoTrim: 视频剪辑（按 start/end 秒数裁剪单段）
#   - videoExtend: 视频续接（v20 bagege：调 Happy Horse V2V `69ef62417f297bdb36eb428b` 续 N 秒）
#   - shotGroup: 多张分镜一致性协调
#   - subtitleRemoval: 视频去字幕
#   - comicSplit: 漫画拆格
#   - preview: 任意上游输出预览
#
# 边的合法连接由前端 edgeValidation 强制（详见 src/modules/video-canvas/edgeValidation.ts）：
#   image.images → image2video.image
#   image.images → image2video.subjectRefs
#   image2video.videoUrl → videoConcat.videos_multi
#   ... 等等
#
# 工作流模板：
#   武侠短片：scriptGen → canvas_expand_shot_table
#     → image（每镜头视觉锚点）→ image2video → videoConcat（时间轴成片）
#

def _post_json(path: str, body: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    """POST JSON to bridge."""
    url = f"{BRIDGE_URL}{path}"
    try:
        response = requests.post(url, json=body, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "url": url}


@mcp.tool()
def canvas_create_project(
    name: str,
    story_beats: str = "",
    character_bible: str = "",
    shot_breakdown: str = "",
    user_confirmed: bool = False,
) -> str:
    """创建一个新的视频项目（含一个空画布）。

    🚧 强制 Phase Gates（v7.2，2026 工业流）：
    在调用此工具前，hermes 必须先在 chat 完整输出三段分析并等用户确认：

    1. **Phase 1 — Story Beats**：题材定位 / 三幕结构 / 情绪曲线 / motif / 钩子句
    2. **Phase 2 — Character Bible**：每个出场角色 ≥200 字，含性格内核、动机、
       微表情、声音设计、Identity Lock 标志物
    3. **Phase 3 — Shot Breakdown**：镜头表（# / 时长 / 节奏 / 内容 / 景别 / 角度 /
       运镜 / 光线 / 色调 / 焦距 / 姿态变化 / SFX），时长由剧情节奏决定（不是
       模型上限填满），含模型选择推理 + 预算估算
    4. **Phase 4 Gate**：用户确认 → 才能调用本工具

    本工具会拒绝缺少 Phase 1-3 文本或未经用户确认的请求，强制工业流程。

    Args:
        name: 项目名，如 "武侠玄幻打斗短片"
        story_beats: Phase 1 输出的剧本拆解全文（≥200 字）
        character_bible: Phase 2 输出的角色 Bible 全文（每角色 ≥200 字）
        shot_breakdown: Phase 3 输出的镜头规划表全文（必须含每镜头时长 + 字段）
        user_confirmed: Phase 4 Gate — 用户确认后才能为 True

    返回 {"projectId": "proj_xxx", "canvasId": "vc_xxx", ...}

    后续所有 canvas_* 调用都需要传这个 projectId。
    """
    # === Phase Gate 硬校验 ===
    missing: list[str] = []
    if len(story_beats.strip()) < 120:
        missing.append(
            "story_beats（Phase 1 剧本拆解，需 ≥120 字符。先在 chat 输出三幕结构 + 情绪曲线 + motif + 钩子句）"
        )
    if len(character_bible.strip()) < 200:
        missing.append(
            "character_bible（Phase 2 角色 Bible，需 ≥200 字符。每个出场角色单独一段含性格内核 / 动机 / 声音 / Identity Lock）"
        )
    if len(shot_breakdown.strip()) < 200:
        missing.append(
            "shot_breakdown（Phase 3 镜头规划，需 ≥200 字符。逐镜头列表含时长 / 景别 / 角度 / 运镜 / 光线 / 色调 / 焦距 / 姿态 / SFX）"
        )
    if not user_confirmed:
        missing.append("user_confirmed=True（Phase 4 Gate — 等用户在 chat 中明确确认后再调用）")

    if missing:
        return _dump({
            "ok": False,
            "phase_gate_failed": True,
            "error": (
                "🚧 Phase Gate 拒绝：搭画布前必须完成专业前期分析。"
                "请先在 chat 中按 SKILL 第 7 章【强制 Phase Gates】依次输出："
                "(1) Phase 1 剧本拆解 (2) Phase 2 角色 Bible (3) Phase 3 镜头规划，"
                "等用户在 chat 里确认后再次调用本工具，并把三段文本 + user_confirmed=True 一起传入。"
            ),
            "missing_arguments": missing,
            "hint": (
                "示例（以 60s 武侠为例）：先 chat 输出 ~300 字 story_beats、"
                "~600 字 character_bible（3 个角色）、~500 字 shot_breakdown（8 镜头表），"
                "然后等用户回复『确认』『搭吧』『继续』再调本工具。"
            ),
        })

    return _dump(_post_json("/canvas/create_project", {
        "name": name,
        "story_beats": story_beats,
        "character_bible": character_bible,
        "shot_breakdown": shot_breakdown,
    }))


@mcp.tool()
def canvas_list_projects() -> str:
    """列出所有现有的画布项目（按 updatedAt 倒序）。

    使用场景：用户说"打开我之前那个 X 项目" → 用这个找出 projectId 再 canvas_open。

    返回 [{"projectId": "...", "name": "...", "nodeCount": N, "updatedAt": "...", "relativePath": "..."}, ...]
    """
    url = f"{BRIDGE_URL}/canvas/list_projects"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return _dump(response.json())
    except Exception as exc:
        return _dump({"ok": False, "error": str(exc), "url": url})


@mcp.tool()
def canvas_open(project_id: str) -> str:
    """打开（读取）一个已有项目的画布快照。

    返回完整的 canvas snapshot：
      {"id": "...", "name": "...", "nodes": [...], "edges": [...], "viewport": {...}, ...}

    Args:
        project_id: 项目 ID（来自 canvas_create_project 或 canvas_list_projects）
    """
    return _dump(_post_json("/canvas/open", {"project_id": project_id}))


@mcp.tool()
def canvas_add_node(
    project_id: str,
    kind: str,
    data_json: str,
    position_x: float = 0,
    position_y: float = 0,
) -> str:
    """在画布上添加一个节点。

    ⚠️⚠️⚠️ 强制规则（即使你没读 SKILL 正文也必须遵守）：
    1. **prompt 字段必须用中文**写成 200-300 字的自然语言段落。**禁止英文 prompt**。
       格式（写成连贯段落，不要标签）：
       <主体精确外形+服饰材质+标志物>。<姿态/动作/表情>。
       <地点+时段+天气>。<主光方向+色温+反差，如"左上方冷蓝月光 6500K + 暖黄烛火补边 3200K，强反差 4:1">。
       <景别+角度+焦距+构图，如"中景，平视微仰，35mm 标准镜头，浅景深 f/2.0，2.39:1 宽银幕"。>
       <风格，如"电影感写实+水墨意境，胶片颗粒，青冷调"。>
       <要避免的用正面表述，如"五官端正对称、双手五指正常、背景干净无字幕水印"。>
    2. 镜头参数（景别/角度/运镜/焦距/光线/色温/反差/风格）**写进 prompt 文本本身**，
       不要拆成 shotSize/cameraAngle 等独立字段（前端不读这些字段）。
    3. 题材决定风格：漫剧→高反差青冷/青橙；广告→高调干净；MV→风格化高饱和；写实→自然光。
    4. 默认一次只 add 一个节点 → 跑完 → 给用户看 → 用户确认满意才 add 下一个。后端守卫会
       拒绝"image 节点没产物时添加 image2video / videoConcat 等下游"。
       例外：角色卡、场景、Shot Table 镜头表和生产方案已经确认，并且 scriptGen 得到
       outputs.scenes 后，标准视频生产线必须用 canvas_expand_shot_table
       受控补齐，不要手工批量 add/connect。这个例外不能跳过角色卡、场景、生产方案选择和必要的参考图连线。

    **核心工具** — hermes 用这个搭起整个 pipeline。**严格按 data 字段约定填，
    多余字段会被忽略 / 节点无法运行（前端只读各 kind 实际定义的字段）。**

    Args:
        project_id: 项目 ID
        kind: 节点类型，必须是以下之一：
            scriptGen / text / image / inpaint / upscale /
            image2video / audio2video / tts / videoConcat / videoTrim / videoExtend /
            musicGen / shotGroup / subtitleRemoval / comicSplit / preview
        data_json: 节点初始 data 的 JSON 字符串。**真实可用字段（与前端 1:1 对齐）**：

            ── scriptGen
            {"prompt": "故事概念", "sceneCount": 6, "model"?: "..."}

            ── text （独立 prompt / 反推结果 / 笔记，可输出给下游 image / image2video 覆盖 prompt）
            {"text": "<提示词或笔记内容>", "role"?: "prompt" | "reverse-prompt" | "note"}

            ── image （**主力 — 角色三视图 / 角色板 / 场景 / 道具 / 镜头静帧 / 风格锚 全用这个**）
            {"prompt": "<200-300 字 中文 自然语言结构化描述（按上面强制规则 1 的格式）>",
             "imageModel": <见下方 v20 imageModel 选型表>,
             "aspectRatio": "16:9" | "9:16" | "1:1" | "21:9",
             "count": 1}
            ⚠ **没有 description / name / viewCount / shotSize / cameraAngle / cameraMovement**
               **/ lighting / colorTone / lens / styleRef 这些字段**。镜头/光线/构图全部
               **写进 prompt 文本本身**，作为自然语言段落的一部分。
            ⚠ 角色锁定（脸/发/服饰/标志物）也写在 prompt 段落里，不要拆字段。

            **v20 imageModel 选型表**（hermes 按场景挑）：

            | 场景 | v20 bagege model id | 积分/次 |
            |---|---|---|
            | 草图 / 大量 draft / 4K 概念稿 | `bs-gpt-image-2-4K` | 25 |
            | 草图 / 大量 draft（标准 1K） | `bs-gpt-image-2` | 8 |
            | 中等质量 / 2K | `bs-gpt-image-2-2K` 或 `bggai-nano-banana-2-text-to-image-v1` | 16 / 12 |
            | **主力档**（分镜/角色三视图） | `bggai-nano-banana-pro-text-to-image-v1` | 22 |
            | 便宜主力（无 4K 需求） | `bggai-nano-banana-text-to-image-v1` | 6 |
            | 高保真 4K | `bs-nano_banana_pro-4K` | 30 |
            | 2K 性价比 | `bs-nano_banana_pro-2K` 或 `bggai-nano-banana-pro-text-to-image-v1` | 25 / 22 |

            协议（v20 — bagege）：POST `{image_base}/images/generations` 提交 JSON body
            （**绝不要**用 multipart），提交后 202 task，轮询 `GET {image_base}/tasks/{id}` 拿 url。
            **绝不要**写 `response_format: "b64_json"`（bagege 不支持，提交后会被忽略）。

            ── inpaint （局部重绘）—— v20 bagege
            {"prompt": "<中文重绘描述>", "maskUrl": "<画布笔刷生成的掩码图>",
             "imageModel": "bggai-nano-banana-image-to-image-v1" | "bggai-nano-banana-pro-image-to-image-v1"}
            （6 / 22 积分/次，bagege 走 image-to-image 路径，input_keys 用 `image_references`）

            ── upscale —— v20 bagege
            {"enhancePrompt": "<可空，额外美化提示>",
             "imageModel": "bs-nano_banana_pro-4K" | "bggai-nano-banana-pro-image-to-image-v1"}
            （30 / 22 积分/次，4K 输出走 bs-nano_banana_pro-4K）

            ── image2video （图生视频）—— v20 bagege
            {"prompt": "<300-500 字 中文 — 只描述运动+变化+单一镜头运动+动作弧线+Foley>",
             "duration": 5 | 6 | 7 | 8 | 9 | 10,
             "videoModel": <见下方 v20 videoModel 选型表 + 4-mode 自动 dispatch 表>,
             "aspectRatio"?: "16:9" | "9:16" | "21:9",
             "audioRef"?: "<可选音频参考 URL，仅 V2V/Happy Horse 有效>",
             "subjectRefs"?: ["<URL1>", "<URL2>", "<URL3>"]}  # ≤3 张，仅 Happy Horse V2V 模式用

            **v20 videoModel 选型表**（hermes 按场景挑——**先调 canvas_list_video_models() 看 default 字段**）：

            | 场景 | v20 bagege model id | 积分/段 | 限制 |
            |---|---|---|---|
            | T2V 文生视频（探索 / Animatic 草稿） | `69ef62417f297bdb36eb4288` | 250 | Happy Horse T2V |
            | **I2V 图生视频**（90% 镜头 — 主力） | `69ef62417f297bdb36eb4289` | 250 | Elo 1392 行业第一 |
            | V2V 视频生视频 / 视频编辑 | `69ef62417f297bdb36eb428b` | 250 | Happy Horse V2V |
            | 字节即梦 2.0 满血（T2V/I2V/V2V 全支持） | `bggai-seedance-2-0-image-to-video-v1` | 220（会员专属，高峰期排队） | 同一 model id 按参数自动 dispatch |

            **4-mode 自动 dispatch 表**（v20 — mode 由连入端口自动决定，**不可手动设**）：

            | 模式 | 触发条件 | 哪些 model 支持 | Rust 后端 images 数组 |
            |---|---|---|---|
            | `text2video` | 啥都不连 | Happy Horse T2V (`...4288`) / Seedance 2.0 | `[]`（空，纯 prompt） |
            | `first-frame` (i2v) | 只连 image | Happy Horse I2V (`...4289`) / Seedance 2.0 | Happy Horse: `image_url`; Seedance: `image_references` |
            | `frames` (ff) | image + tailFrame | **v20 无 model 支持**（Happy Horse / Seedance 都不接 tailFrame 字段）| — |
            | `components` (ref) | 只连 subjectRefs | Happy Horse V2V / Seedance 2.0 | `[ref1..3]` |
            | 实际 V2V | 上游 videoUrl + reference_image_urls | Happy Horse V2V (`...428b`）| `video_url + reference_image_urls` |

            **关键约束**：
            - Seedance 2.0（`bggai-seedance-2-0-image-to-video-v1`）T2V/I2V/V2V 全支持，同一 model id 按参数自动 dispatch，不再有任何模式限制
            - 协议（v20 — bagege）：POST `{video_base}/videos/generations`（**注意 /generations 后缀**），提交后 202 task，轮询 `GET {video_base}/tasks/{id}` 拿 url（**不是**诗云的 `/videos/{id}`）
            - 绝不要用诗云 model id（`veo3.1-*` / `sora-2` / `kling-video` / `MiniMax-Hailuo` / `viduq*` / `wan2.*`）——已停服

            ── audio2video （**v20 数字人降级**——bagege 暂未挂 kling-avatar 数字人变体）
            **硬约束**：视频节点 100% 不与诗云有关系。audio2video 节点默认改走
            bagege Happy Horse V2V 模式（用上游 audio + character 图驱动生视频，
            5-10s 同步音视频，**不是真"口型同步"——是 V2V 模式**）。
            后续 bagege 上挂 avatar 变体后可改回。
            {"videoModel": "69ef62417f297bdb36eb428b"}  # Happy Horse V2V
            // 输入：audio handle（来自 tts.audioUrl）+ character handle（来自 image.images）

            ── tts （**chat 继续诗云**——TTS 走诗云 minimax-audio）
            {"text": "<对白原文>", "voice": "alloy" | "nova" | "echo" | ...,
             "audioModel": "minimax-audio"}
            // v20 暂未挂 bagege audio 渠道；chat/audio 业务继续走诗云

            ── musicGen （**v20 暂未挂 bagege audio**——保留诗云 audio1.0）
            {"prompt": "<中文音乐风格描述>", "duration": 60, "audioModel": "audio1.0" | "kling-audio",
             "timingPrompts"?: [{"from": 0, "to": 3, "prompt": "..."}, ...]}
            // 诗云 vidu audio1.0 / 可灵音频。bagege 暂未挂 audio 渠道

            ── videoConcat （成片）
            {"videoOrder": ["<videoNodeId1>", "<videoNodeId2>", ...],
             "crossfadeSeconds"?: 0.3, "reencode"?: true,
             "bgmUrl"?: "...", "bgmVolume"?: 0.35,
             "cutPattern"?: "rapid-cut" | "j-cut" | "l-cut" | "montage" | "standard",
             "segmentTrims"?: {"<sourceVideoNodeId>": {"startSec": 0, "endSec": 5}}}

            ── videoTrim    {"startSec": 0, "endSec": 5, "reencode"?: true}
            ── videoExtend  {"prompt": "中文续接描述", "extendSeconds": 5,
                             "videoModel": "69ef62417f297bdb36eb428b"}  # Happy Horse V2V
                             // v20 默认走 Happy Horse V2V 模式（prompt 驱动）
            ── subtitleRemoval  {"region": "<区域描述>"}
            ── comicSplit  {"imageUrl": "<漫画图 URL>"}
            ── shotGroup  {"memberNodeIds": [...], "coherencePrompt": "中文协调风格",
                           "imageModel": "bggai-nano-banana-pro-text-to-image-v1"}
                           // v20 默认 22 积分/张 的 BggAI NanoBananaPro 主力档
            ── preview  {}

        position_x, position_y: 节点位置；不给则自动叠右下方

    返回 {"nodeId": "node_xxx"}
    """
    try:
        data = json.loads(data_json) if data_json.strip() else {}
    except json.JSONDecodeError as e:
        return _dump({"ok": False, "error": f"data_json 不是合法 JSON: {e}"})
    body: dict[str, Any] = {
        "project_id": project_id,
        "kind": kind,
        "data": data,
    }
    if position_x or position_y:
        body["position_x"] = float(position_x)
        body["position_y"] = float(position_y)
    return _dump(_post_json("/canvas/add_node", body, timeout=30))


@mcp.tool()
def canvas_connect(
    project_id: str,
    src_node_id: str,
    src_handle: str,
    tgt_node_id: str,
    tgt_handle: str,
) -> str:
    """把两个节点连起来。

    **必须严格遵守合法连接规则**（与前端 edgeValidation.ts + 后端 is_legal_edge 1:1 对齐）。
    后端有渐进守卫：源节点 outputs 为空时连下游会被拒绝（除 text→prompt、image→reference）。

    ── image 输出（handle = "images"）→
        → image2video.image      (首帧)
        → image2video.tailFrame  (末帧，双关键帧锁定)
        → image2video.subjectRefs (角色锚点 / contact sheet)
        → image.reference        (跨图锁角色)
        → inpaint.image / upscale.image
        → audio2video.character
        → shotGroup.boards_multi
        → comicSplit.image
        → preview.any

    ── text 输出（handle = "text"，覆盖下游 prompt）→
        → image.prompt
        → image2video.prompt
        → musicGen.prompt
        → preview.any

    ── inpaint / upscale 输出（handle = "imageUrl"）→
        → image2video.image / .tailFrame / .subjectRefs
        → upscale.image / inpaint.image
        → image.reference
        → preview.any

    ── tts / musicGen 输出（handle = "audioUrl"）→
        → audio2video.audio
        → preview.any

    ── image2video / audio2video 输出（handle = "videoUrl"）→
        → videoConcat.videos_multi
        → videoTrim.video / videoExtend.video / subtitleRemoval.video
        → preview.any

    ── videoConcat / videoTrim / videoExtend / subtitleRemoval 互相串联（videoUrl）→
        videoConcat.videoUrl → videoTrim/videoExtend/subtitleRemoval/preview
        videoTrim/videoExtend/subtitleRemoval.videoUrl → 同上 + videoConcat.videos_multi

    ── shotGroup 输出（handle = "boards"）→ image2video.image / preview.any
    ── comicSplit 输出（handle = "panels"）→ image2video.image / shotGroup.boards_multi / preview.any

    ⚠ **不存在** "subjectRefs" / "views" / "boards" / "scenes" / "styleRef" / "characters" 等作为
       源 handle —— 这些都是 **target handle**。源 handle 只有 "images" / "imageUrl" / "videoUrl"
       / "audioUrl" / "text" / "boards" / "panels" 这几种。

    Args:
        project_id: 项目 ID
        src_node_id, src_handle: 源节点 ID + 输出 handle 名
        tgt_node_id, tgt_handle: 目标节点 ID + 输入 handle 名

    返回 {"edgeId": "edge_xxx"}
    """
    return _dump(_post_json("/canvas/connect", {
        "project_id": project_id,
        "src_node_id": src_node_id,
        "src_handle": src_handle,
        "tgt_node_id": tgt_node_id,
        "tgt_handle": tgt_handle,
    }, timeout=30))


@mcp.tool()
def canvas_update_node_data(
    project_id: str,
    node_id: str,
    patch_json: str,
) -> str:
    """修改节点的 data 字段（部分更新）。

    使用场景：建好画布后想改 prompt / 模型 / 时长，不重建节点。

    Args:
        project_id: 项目 ID
        node_id: 节点 ID
        patch_json: JSON 字符串，只包含要改的字段，例：
            '{"prompt": "新的描述"}' 只改 prompt
            '{"imageModel": "bggai-nano-banana-pro-text-to-image-v1"}' 只改模型（v20 bagege）
            '{"videoModel": "69ef62417f297bdb36eb4289"}' 只改视频模型（v20 bagege）
            '{"duration": 12}' 只改视频时长
    """
    try:
        patch = json.loads(patch_json) if patch_json.strip() else {}
    except json.JSONDecodeError as e:
        return _dump({"ok": False, "error": f"patch_json 不是合法 JSON: {e}"})
    return _dump(_post_json("/canvas/update_node_data", {
        "project_id": project_id,
        "node_id": node_id,
        "patch": patch,
    }, timeout=30))


@mcp.tool()
def canvas_delete_node(project_id: str, node_id: str) -> str:
    """删除画布上的一个节点，同时删除所有与之关联的边和节点生成的媒体文件。

    使用场景：用户说"删除这个节点" / "把 X 节点删掉" → 用这个工具。

    注意：
      - 删除节点时会自动删除所有与该节点相连的边
      - 删除节点时也会删除该节点生成的媒体文件（_node_outputs/<node_id>/）
      - 删除后画布快照会自动更新
      - 如果节点有运行中的任务，请先确认已停止

    Args:
        project_id: 项目 ID
        node_id: 节点 ID（来自 canvas_open 或 canvas_get_state）

    返回更新后的完整画布快照：{"nodes": [...], "edges": [...], ...}
    """
    return _dump(_post_json("/canvas/delete_node", {
        "project_id": project_id,
        "node_id": node_id,
    }, timeout=30))


@mcp.tool()
def canvas_delete_node_output(project_id: str, node_id: str) -> str:
    """删除画布上指定节点生成的媒体文件（保留节点本身，只清输出）。

    使用场景：
      - 用户说"清除这个节点生成的图片" / "删除这个节点的输出"
      - 节点已完成生成，但用户想重新生成或释放空间

    注意：
      - 只删除节点生成的媒体文件，节点本身和画布连线保持不变
      - 节点 status 会重置为 "idle"，下次运行时会重新生成

    Args:
        project_id: 项目 ID
        node_id: 节点 ID（来自 canvas_get_state）

    返回操作结果
    """
    return _dump(_post_json("/canvas/delete_node_output", {
        "project_id": project_id,
        "node_id": node_id,
    }, timeout=30))


@mcp.tool()
def canvas_delete_edge(project_id: str, edge_id: str) -> str:
    """删除画布上的一条边（断开两个节点之间的连接）。

    使用场景：用户说"删除这条连线" / "断开 X 和 Y 的连接" → 用这个工具。

    注意：
      - 只删除边本身，不影响节点
      - 删除后画布快照会自动更新

    Args:
        project_id: 项目 ID
        edge_id: 边 ID（来自 canvas_open 或 canvas_get_state 中的 edges 数组）

    返回更新后的完整画布快照：{"nodes": [...], "edges": [...], ...}
    """
    return _dump(_post_json("/canvas/delete_edge", {
        "project_id": project_id,
        "edge_id": edge_id,
    }, timeout=30))


@mcp.tool()
def canvas_get_state(project_id: str) -> str:
    """获取当前画布状态（节点 + 边 + 每节点 status / outputs）。

    使用场景：
      - 搭完画布后给用户看一眼整体结构
      - 查询某节点是否生成完成（status == "done"）
      - 决定下一步该跑哪个节点

    返回完整 snapshot：{"nodes": [...], "edges": [...], ...}
    每个 node 含 data.status: "idle" | "queued" | "running" | "done" | "error"
    """
    return _dump(_post_json("/canvas/get_state", {"project_id": project_id}, timeout=30))


@mcp.tool()
def canvas_expand_shot_table(project_id: str, script_node_id: str = "") -> str:
    """🆕 Shot Table 核心通道：从 scriptGen.outputs.scenes 展开标准视频生产流水线。

    使用时机：
      1. 先按 Skill 原流程完成角色卡/角色板、场景、道具，并通过 Shot Table 镜头表 review gate。
      2. 再用 canvas_add_node(kind="scriptGen") 创建脚本/Shot Table 节点。
      3. 用 canvas_run_node(project_id, script_node_id, mode="only") 跑出 outputs.scenes。
      4. 让用户选择生产方案：故事板参考 / 首尾帧 / Ingredients-Components / 草稿 Animatic / 参考视频迁移。
      5. 调本工具受控展开：
         scriptGen → image(每镜头视觉锚点) → image2video(每镜头视频) → videoConcat(成片时间轴)。

    这个工具是普通渐进守卫的安全例外：它只基于已经生成出的 Shot Table 工作，
    会给每个节点写入 sceneId/sourceScriptId 元数据并保持幂等，不要手工批量 add/connect。
    它是“补生产线”工具：按 Shot Table 创建每镜头视觉锚点、视频段和成片时间轴。
    如果选择故事板参考模式，展开后必须把故事板总览板、角色、场景、道具图继续连到
    image2video.subjectRefs；故事板不只是说明图。这个工具不是跳过角色卡、场景、
    生产方案或参考图连线直接生成视频的捷径。

    返回：
      {
        "scriptNodeId": "...",
        "imageNodeIds": ["..."],      // 按镜头顺序；逐个 canvas_run_node(..., mode="only") 跑视觉锚点
        "videoNodeIds": ["..."],      // 视觉锚点 / 参考图连线确认后逐个跑视频
        "concatNodeId": "...",        // 最后跑成片；可先用 canvas_update_node_data 改时间轴
        "addedNodeCount": 0,
        "addedEdgeCount": 0
      }
    """
    body: dict[str, Any] = {"project_id": project_id}
    if script_node_id.strip():
        body["script_node_id"] = script_node_id.strip()
    return _dump(_post_json("/canvas/expand_shot_table", body, timeout=30))


# ─── v7 新增：画布级 meta（自检开关、影视级模式开关）────────────────

@mcp.tool()
def canvas_get_meta(project_id: str) -> str:
    """读画布级 meta 设置（自检 / 影视级模式 等开关）。

    返回 {
      "selfCheckEnabled": false,        // hermes 跑完节点是否自动调 evaluate_artifact 审核
      "selfCheckMaxRetries": 3,          // 自检失败时自动改 prompt 重跑的最大次数
      "selfCheckPassThreshold": 8,       // vision 评分 >= 此值算通过（满分 10）
      "cinematicProMode": false          // 影视级深度模式：beat sheet / multi-ref / 双比例
    }
    """
    return _dump(_post_json("/canvas/get_meta", {"project_id": project_id}, timeout=10))


@mcp.tool()
def canvas_set_self_check(
    project_id: str,
    enabled: bool,
    max_retries: int = 3,
    pass_threshold: int = 8,
) -> str:
    """启停 hermes 的视觉自检闭环。

    **何时启用**:
      - 用户说"严格审核"/"质量优先"/"完美一致性"
      - 重要项目（影视级、节展投递）
      - 角色或风格特别复杂、容易漂移

    **何时关闭**（**默认**）:
      - 普通项目，用户希望快速出片
      - vision 配额紧张
      - 用户说"不用审了" / "我自己看"

    启用后的行为：
    - 跑完每个 image / image2video 节点后，hermes 自动调
      canvas_evaluate_artifact 审核一致性
    - 评分 >= pass_threshold (默认 8/10) 视为通过
    - 评分 < threshold 时自动改 prompt 并 canvas_run_node 重跑（最多 max_retries 次）
    - 重试用尽仍不达标 → 告诉用户具体失败原因，不自动重跑

    Args:
        project_id: 项目 ID
        enabled: True 启用 / False 关闭
        max_retries: 自检失败时自动重跑的最大次数（1-5），默认 3
        pass_threshold: 通过的最低分（5-10），默认 8

    返回当前完整 meta（变化后的状态）
    """
    if max_retries < 1 or max_retries > 5:
        return _dump({"ok": False, "error": "max_retries 必须在 1-5 范围内"})
    if pass_threshold < 5 or pass_threshold > 10:
        return _dump({"ok": False, "error": "pass_threshold 必须在 5-10 范围内"})
    patch = {
        "selfCheckEnabled": bool(enabled),
        "selfCheckMaxRetries": int(max_retries),
        "selfCheckPassThreshold": int(pass_threshold),
    }
    return _dump(_post_json("/canvas/set_meta", {
        "project_id": project_id,
        "patch": patch,
    }, timeout=10))


@mcp.tool()
def canvas_set_cinematic_pro_mode(project_id: str, enabled: bool) -> str:
    """启停影视级深度模式（cinematic pro mode）。

    **启用后 hermes 会额外做**：
    1. Beat Sheet 三幕结构前置规划
    2. 9 视图 multi-reference stack（角色 9 张参考全部注入下游）
    3. 关键镜头 A/B 变体（hook / climax / final 各 3 版）
    4. 横屏 + 竖屏双成片输出
    5. Continuity rules（180° / eye-line / action match / no grade shift）
    6. Look Dev 试拍循环（先确认前 1-2 镜头风格再批量出）

    **配额消耗**：约为标准模式的 2.5×（多变体 + 多比例）

    **何时启用**:
      - 用户说"影视级 / 电影级 / 大片质感"
      - 用户说"上电影院 / 提交节展 / 商业项目"
      - 多角色（≥3）或长片（>90s）

    Args:
        project_id: 项目 ID
        enabled: True 启用 / False 关闭

    返回当前完整 meta
    """
    return _dump(_post_json("/canvas/set_meta", {
        "project_id": project_id,
        "patch": {"cinematicProMode": bool(enabled)},
    }, timeout=10))


@mcp.tool()
def canvas_list_video_models() -> str:
    """列出所有可用视频模型 + 它们的真实能力（v20 — bagege）。

    **v20 关键变化**：
    - 视频供应商已切到 bagege（https://www.bagege.cn），**诗云的 veo/sora/kling/hailuo/wan/vidu/gpt-image-1 全停服**
    - 返回 4 个 model：3 个 Alibaba Happy Horse（T2V / I2V / V2V）+ 1 个字节即梦 2.0 满血（T2V/I2V/V2V 全支持）
    - "default" 字段是 v20 推荐默认（Happy Horse I2V），**用 default 字段做 fallback，不要硬编码 model id**

    **hermes 调用流程**（必读）：
    ```
    1. canvas_list_video_models() → 拿到 4 个 model + 各自动态
    2. 按"本段需求"过滤（见决策规则）
    3. canvas_run_node(image2video_node) 实际跑（v20 走 bagege JSON 协议 + /tasks/{id} 轮询）
    ```

    返回结构（v20 — bagege）：
    {
      "providers": [
        {
          "id": "bagege-alibaba-happy-horse",
          "label": "Alibaba Happy Horse 1.0 (bagege)",
          "models": [
            {
              "id": "69ef62417f297bdb36eb4288",     // T2V 文生视频（唯一支持 T2V）
              "label": "Happy Horse T2V",
              "durationsSeconds": [5,6,7,8,9,10],   // 5-10s 灵活
              "tailFrame": false,                  // 不支持尾帧锚定
              "nativeAudio": true,                  // 同步音视频（开源 Elo 第一）
              "maxResolution": "1080p",
              "modes": ["text-to-video"],           // 唯一支持 T2V
              "priceCredits": 250,
              "notes": "POST {base}/videos/generations + GET {base}/tasks/{id} 轮询"
            },
            {
              "id": "69ef62417f297bdb36eb4289",     // I2V（**v20 默认 + 主力**）
              "label": "Happy Horse I2V",
              "durationsSeconds": [5,6,7,8,9,10],
              "tailFrame": false,
              "nativeAudio": true,
              "modes": ["first-frame-only"],
              "priceCredits": 250,
              "notes": "Elo 1392 行业第一；任何"有上游图、走 I2V"都用这个"
            },
            {
              "id": "69ef62417f297bdb36eb428b",     // V2V 视频生视频
              "label": "Happy Horse V2V",
              "durationsSeconds": [5,6,7,8,9,10],
              "modes": ["components-only"],          // 实际是"上游 video + reference images"
              "priceCredits": 250,
              "notes": "videoExtend 节点也走这个（prompt 驱动，不需要上游 taskId）"
            }
          ]
        },
        {
          "id": "bagege-bggai-seedance",
          "label": "BggAI 即梦 2.0 满血 (bagege · T2V/I2V/V2V 全支持)",
          "models": [
            {
              "id": "bggai-seedance-2-0-image-to-video-v1",
              "label": "即梦 2.0 满血 (T2V/I2V/V2V)",
              "durationsSeconds": [4,5,6,7,8,9,10,11,12,13,14,15],  // 4-15s 灵活
              "aspectRatios": ["16:9","9:16","1:1","4:3","3:4","2.39:1"],
              "priceCredits": 220,
              "modes": ["text-to-video", "first-frame-only", "components-only"],  // 同一 model id 全模式支持
              "notes": "T2V/I2V/V2V 全支持; image 输入走 image_references（不是 image_url）; input_keys: prompt, image_references, video_url, aspect_ratio, duration, resolution"
            }
          ]
        }
      ],
      "default": "69ef62417f297bdb36eb4289"  // Happy Horse I2V（v20 推荐默认）
    }

    **决策规则（v20 bagege）—— hermes 选 model 时按顺序检查**：

    1. **是否需要 T2V / V2V 模式**？→ Happy Horse T2V (`69ef62417f297bdb36eb4288`) / V2V (`69ef62417f297bdb36eb428b`) 或 Seedance 2.0（同一 model id 全模式支持）均可。
    2. **I2V 模式**（90% 镜头）→ 首选 `69ef62417f297bdb36eb4289`（Happy Horse I2V，**v20 默认**）。
       用户明说"用字节即梦"才切 `bggai-seedance-2-0-image-to-video-v1`（220 积分/次）。
    3. **时长 >10s**（11-15s）→ Happy Horse 仅 5-10s，切 `bggai-seedance-2-0-image-to-video-v1`（4-15s）。
    4. **4K 视频** → bagege v20 没 4K model（最高 1080p），告诉用户等 bagege 后续 model。
    5. **首尾帧（first-tail-frame）模式** → bagege 上**没有 model 支持**（Happy Horse 不接 tailFrame 字段）。
       如必须用 → 退到 V2V 模式 `69ef62417f297bdb36eb428b`，把 tailFrame 抽出为 reference_image_urls。
    6. **数字人对位**（audio2video 节点）→ audio2video v20 默认 `69ef62417f297bdb36eb428b`（Happy Horse V2V 模式降级），
       数字人对位效果会降级（不是真"口型同步"）。等 bagege 后续挂 avatar 变体再切回。
    7. **性价比** → Happy Horse I2V（250 积分/段）+ BS GPT-Image-2（8 积分/张）。
    8. **同步音视频**（v20 全部 model 都支持）→ Happy Horse 系列（行业独家同步音视频生成）。

    **硬约束清单**（v20 — 违反任意一条都跑不通）：

    - ❌ **绝不要**写诗云 model id（`veo3.1-*` / `sora-2` / `kling-video` / `MiniMax-Hailuo` / `viduq*` / `wan2.*` /
       `doubao-seedance-2-0-260128` / `happyhorse-1.*`）——诗云 video/image model 已停服，会 503
    - ❌ **绝不要**用 `b64_json` 字段（bagege 不支持，提交后 bagege 会忽略）
    - ❌ **绝不要**用 multipart 上传（bagege 走纯 JSON body，所有 `*_bytes` / `*_mime` 都是 None）
    - ✅ **必须**用 `aspect_ratio: "16:9"` / `resolution: "1080p"`（bagege 字段名）
    - ✅ **必须**轮询 `GET {base}/tasks/{id}`（不是诗云的 `/videos/{id}`）
    - ✅ **必须**提交后等 202 task，不要假设同步返回
    """
    body = _request_json("GET", "/canvas/list_video_models", params={})
    return _dump(body)


@mcp.tool()
async def canvas_run_node(
    project_id: str,
    node_id: str,
    mode: str = "downstream",
) -> str:
    """**后端同步运行节点 — 真正出图/出视频**（v19，不再依赖前端）。

    Args:
        project_id: 项目 ID
        node_id: 要运行的节点 ID
        mode: 运行模式
            - "only": 只跑这一个节点（推荐：渐进式，一次一个）
            - "downstream": 跑这个节点 + 缺失上游 + 下游
            - "full": 跑整张画布

    **同步执行**：本工具会**一直等到节点跑完才返回**（图片 ~30s，视频 ~4min），
    返回里直接带每个节点的结果，无需再轮询。返回结构：
      {"projectId": "...", "ok": true/false,
       "ran": [{"nodeId": "...", "kind": "image", "status": "done",
                "outputSummary": "images",
                "displayMarkdown": "![生成图](Canvas/_generated/xxx.png)",
                "outputUrls": ["Canvas/_generated/xxx.png"]},
               {"nodeId": "...", "kind": "image2video", "status": "error",
                "error": "失败原因"}]}

    拿到结果后：
      - status == "done" → **直接把该节点的 `displayMarkdown` 字段原样粘进你的回复**
        给用户看（它已经是 `![名字](url)` / `🎬 [名字](url)` 格式，对话区会自动
        渲染出图片/视频/音频）。⚠️ **绝对不要**用 terminal / open / 命令行去打开
        本地图片浏览器 —— 用户要在对话里看，不是在系统看图器里看。
      - 若没有 displayMarkdown（少数节点），再调 canvas_get_state(project_id) 取该节点
        data.outputs 里的 URL 自己拼 `![](url)`。
      - status == "error" → 读 error 字段告诉用户失败原因并修复（如 prompt 为空、
        prompt 非中文被语言守卫拒绝、上游没连图等）。

    **重要**：
      - 真实调用图/视频 API，消耗配额。一次只跑一个节点（mode="only"），
        跑完贴给用户看、等用户确认满意，再跑下一个。
      - 后端会先把 status 写成 running、跑完写 done/error，前端画布开着也会实时看到。
    """
    payload = {
        "project_id": project_id,
        "node_id": node_id,
        "mode": mode,
    }
    result = await asyncio.to_thread(
        _post_json,
        "/canvas/run_node_sync",
        payload,
        600,
    )
    return _dump(result)


# ─── 辅助工具：长剧本拆解 / 自评 / 落盘 / 列产物 ─────────────

@mcp.tool()
def canvas_segment_script(
    raw_script: str,
    target_episodes: int = 0,
    target_seconds_per_episode: int = 60,
    chat_model: str = "",
) -> str:
    """**长剧本拆解**——把任意长度剧本/小说/故事概念拆成可生产的「分集 → beats」结构。

    什么时候用：
      - 用户给的剧本 > 500 字，或
      - 用户说"做成多集 / 一系列 / 一个剧"，或
      - 任何复杂故事开始时（避免直接生产）

    返回 JSON：episodes / global_characters / global_style 三大字段，hermes 应该
    根据它在画布上 add_node：
      - 给 global_characters 每人建 image 节点
      - 给 episodes[*].beats[*] 每场建 image 节点
      - 然后 connect image.images → image2video.subjectRefs / .image

    Args:
        raw_script: 原始剧本/概念
        target_episodes: 0 = 让模型按字数推荐
        target_seconds_per_episode: 每集时长（秒）
        chat_model: 默认 gpt-4o-mini
    """
    body = {
        "raw_script": raw_script,
        "target_episodes": int(target_episodes),
        "target_seconds_per_episode": int(target_seconds_per_episode),
        "chat_model": chat_model or None,
    }
    return _dump(_post_json("/canvas/segment_script", body, timeout=300))


@mcp.tool()
def canvas_evaluate_artifact(
    artifact_url: str,
    brief: str,
    expected_character_desc: str = "",
    expected_style: str = "",
    chat_model: str = "",
) -> str:
    """视觉自评 — 用 vision 模型看一张图是否符合 brief。

    **仅对图像有效**。视频 URL 会自动 skipped（多数 vision 网关不支持 mp4）。

    **何时调用**（v7）：
      - 仅当 canvas_get_meta 返回 selfCheckEnabled=true 时才主动调
      - 跑完一个 image / image2video 节点后，看产物是否符合：
        * 角色一致性: face / hair / outfit / signature 与 角色锚点图对齐
        * 镜头执行: 实际景别/角度/运镜匹配指定的 shotSize / cameraMovement
        * 风格统一: 跟整片 image 风格锚对齐
        * Negative 违反: 是否出现字幕 / 水印 / 多手指 / 现代元素
      - 评分 >= meta.selfCheckPassThreshold (默认 8/10) 视为通过
      - 评分 < threshold 时调 canvas_update_node_data 改 prompt + canvas_run_node 重跑
      - 重试上限 = meta.selfCheckMaxRetries（默认 3）

    Args:
        artifact_url: 图像 URL（data: 或 https:）
        brief: 这张图本应实现什么（要具体到 face/hair/outfit/shot 各项审核点）
        expected_character_desc: 主角应该长什么样（可空）
        expected_style: 整片风格句（可空）
        chat_model: 默认 gpt-4o-mini

    返回 {"score": 0-10, "passed": >=7, "issues": [...], "suggestions": "..."}
    视频会返回 {"score": -1, "skipped": true, ...}
    """
    body = {
        "artifact_url": artifact_url,
        "brief": brief,
        "expected_character_desc": expected_character_desc or None,
        "expected_style": expected_style or None,
        "chat_model": chat_model or None,
    }
    return _dump(_post_json("/canvas/evaluate_artifact", body, timeout=180))


@mcp.tool()
def canvas_save_artifact(url: str, relative_path: str) -> str:
    """把某个产物（data URL 或 https URL）保存到 vault 的 Canvas/ 目录。

    使用场景：节点运行完后，把关键产物（三视图同框图 / 最终成片）
    持久化到 vault，让用户能在 Finder 找到。

    Args:
        url: 产物 URL
        relative_path: vault 相对路径，必须以 "Canvas/" 开头，例 "Canvas/wuxia/final.mp4"

    返回 {"absolutePath": "...", "bytes": N}
    """
    return _dump(_post_json("/canvas/save_artifact", {"url": url, "relative_path": relative_path}, timeout=300))


@mcp.tool()
def canvas_list_artifacts(project: str = "") -> str:
    """列出 vault Canvas/ 目录下的所有产物（递归）。

    Args:
        project: 可选项目子目录名。空 = 列全部 Canvas/
    """
    return _dump(_request_json("GET", "/canvas/list_artifacts", params=_clean_params(project=project)))


# ─── v8 — Spawn 子节点 / 主体库 / 一键重排（LibTV 范式对齐） ─────────────


@mcp.tool()
def canvas_get_spawned_children(project_id: str, parent_node_id: str) -> str:
    """🆕 v8 — 拿父节点（image）spawn 出来的所有独立 image 子节点列表。

    LibTV 范式对齐：跑完 image 后会自动 spawn N 个独立 image 子节点
    （每张图都是画布上的独立节点，可单独 inpaint / 重跑 / 当下游 reference）。
    本工具用于查最新批次的子节点列表，包含每个子节点的 ID / 角度标签 / 图片 URL，
    方便你「挑选其中 1-3 张连到 image2video.subjectRefs」「逐个作为 image.reference」
    等下游操作。

    返回：
      {
        "parentNodeId": "...",
        "spawnGenerationId": "...",   # 最新批次 ID（重跑会变）
        "children": [
          {"childNodeId": "...", "spawnIndex": 0, "spawnLabel": "正面", "imageUrl": "...", "status": "done"},
          ...
        ]
      }

    用法：在 canvas_run_node 跑完 image 后，调本工具拿到子节点列表，
    然后用 canvas_connect 把 (childNodeId, "images") → (image2video, "subjectRefs")
    或 → (image, "reference") 等。

    Args:
        project_id: 画布项目 ID
        parent_node_id: 父节点 ID（image 的 ID）
    """
    return _dump(_post_json(
        "/canvas/spawned_children",
        {"project_id": project_id, "parent_node_id": parent_node_id},
    ))


@mcp.tool()
def canvas_clean_old_spawn_batches(project_id: str, parent_node_id: str) -> str:
    """🆕 v8 — 删除非最新批次的子节点，保持画布干净。

    重跑父节点时旧子节点会保留（保护用户的 inpaint / 下游连线）。
    画布上节点太多时调本工具清理。**只删非最新 spawnGenerationId 的子节点，
    最新批次保留不动；已经被用户连进下游的子节点也照样删（连线一起删）**。

    Args:
        project_id: 画布项目 ID
        parent_node_id: 父节点 ID
    """
    return _dump(_post_json(
        "/canvas/clean_old_spawn_batches",
        {"project_id": project_id, "parent_node_id": parent_node_id},
    ))


@mcp.tool()
def canvas_auto_layout(project_id: str) -> str:
    """🆕 v8 — 一键自动重排画布（LibTV `Shift+Option+F` 对应）。

    画布上节点超过 15 个或子节点 spawn 后凌乱时调本工具，
    会按拓扑层级 + 父子血缘整理布局，相当于用户按 Shift+Option+F。

    Args:
        project_id: 画布项目 ID
    """
    return _dump(_post_json("/canvas/auto_layout", {"project_id": project_id}))


# ─── 主体库（人物 / 场景 / 道具）─────────────────────────────────


@mcp.tool()
def canvas_subject_list(type_filter: str = "") -> str:
    """🆕 v8 — 列出主体库的所有主体（跨画布资产，对齐 LibTV 团队主体库）。

    主体分三类：
      - character：人物（含 N 视图）
      - scene：场景
      - prop：道具

    **强烈推荐**：搭画布前先调本工具检索是否已有可复用主体（同一角色 / 同一场景），
    命中就 `canvas_subject_load` + `canvas_op_add_node` 直接落地为 status=done 节点，
    不需要重新生成 → 省时间省积分 + 角色一致性更稳。

    Args:
        type_filter: "" = 全部 / "character" / "scene" / "prop"
    """
    payload: dict = {}
    if type_filter:
        payload["type_filter"] = type_filter
    return _dump(_post_json("/canvas/subjects/list", payload))


@mcp.tool()
def canvas_subject_load(subject_id: str) -> str:
    """🆕 v8 — 读一个主体的完整数据（含所有视图 URL）。

    返回：
      {"id", "type", "name", "description", "coverImageUrl",
       "views": [{"label": "正面", "url": "..."}, ...],
       "imageModel", "tags", "createdAt", "updatedAt"}

    拿到后用 canvas_op_add_node 把 type="character" 的主体落地为
    `kind=image, status=done, outputs.views=[...]` 节点；
    type="scene"/"prop" 落地为 `kind=image, status=done`。

    Args:
        subject_id: 主体 ID（subj_xxx，通常从 canvas_subject_list 拿）
    """
    return _dump(_post_json("/canvas/subjects/load", {"subject_id": subject_id}))


@mcp.tool()
def canvas_subject_save(
    name: str,
    subject_type: str,
    cover_image_url: str,
    views: list,
    description: str = "",
    image_model: str = "",
    tags: list | None = None,
    source_project_id: str = "",
    source_node_id: str = "",
) -> str:
    """🆕 v8 — 把当前画布上的图保存为可跨画布复用的主体。

    用例：用户做了张曼玉风格 9 视图角色立绘后，调本工具存为人物主体；
    下个画布开工时直接 canvas_subject_list / load 复用，不需要重做角色一致性。

    Args:
        name: 主体名（必填）
        subject_type: "character" / "scene" / "prop"
        cover_image_url: 主图 URL（人物用最佳那张正面图，场景/道具直接用单图）
        views: 视图列表 [{"label": "正面", "url": "..."}, ...]。
            人物建议 3-9 张多角度；场景/道具单图也行（views 就传 [cover 一张]）。
        description: 描述（可选）
        image_model: 生成模型 ID（可选，用于跨画布维持模型一致）
        tags: 标签列表（可选，用于检索）
        source_project_id: 来源项目 ID（可选，跨集追踪）
        source_node_id: 来源节点 ID（可选）
    """
    item = {
        "id": "",
        "type": subject_type,
        "name": name,
        "description": description,
        "coverImageUrl": cover_image_url,
        "views": views,
        "imageModel": image_model,
        "tags": tags or [],
        "sourceProjectId": source_project_id or None,
        "sourceNodeId": source_node_id or None,
        "createdAt": "",
        "updatedAt": "",
    }
    return _dump(_post_json("/canvas/subjects/save", {"item": item}))


@mcp.tool()
def canvas_subject_delete(subject_id: str) -> str:
    """🆕 v8 — 删除主体库的某个主体（不影响已经引用过它的画布节点）。"""
    return _dump(_post_json("/canvas/subjects/delete", {"subject_id": subject_id}))


@mcp.tool()
def canvas_spawn_children(
    project_id: str,
    parent_node_id: str,
    children_json: str,
) -> str:
    """🆕 v8 — 批量 spawn N 个独立 image 子节点（原子操作）。

    用例：
      - 跑完 image（自动 spawn）后，hermes 想再加几张额外角度
      - 多模态魔法（temporal/reverse-prompt）跑完拿到结果，要把结果作为新子节点放上画布
      - 需要把外部 URL 列表转成画布上的独立节点

    Args:
        project_id: 项目 ID
        parent_node_id: 父节点 ID（子节点会以它为锚点自动布局）
        children_json: JSON 字符串。结构示例：
          [
            {
              "kind": "image",
              "data": {
                "kind": "image",
                "prompt": "正面视角 - 白衣少年剑仙",
                "imageModel": "bggai-nano-banana-pro-text-to-image-v1",
                "aspectRatio": "1:1",
                "count": 1,
                "status": "done",
                "outputs": {"images": [{"url": "https://..."}]},
                "meta": {
                  "parentNodeId": "<父 id>",
                  "parentKind": "image",
                  "spawnLabel": "front",
                  "spawnSource": "hermes-manual"
                }
              },
              "position": [800, 200]
            },
            ...
          ]

    返回 {"childNodeIds": [...], "spawnGenerationId": "gen_xxx"}

    注意：spawn 出去的子节点是独立节点，可以单独编辑/重跑/连下游。
    """
    try:
        children = json.loads(children_json) if children_json.strip() else []
    except json.JSONDecodeError as e:
        return _dump({"ok": False, "error": f"children_json 不是合法 JSON: {e}"})
    if not isinstance(children, list):
        return _dump({"ok": False, "error": "children_json 必须是数组"})
    return _dump(_post_json("/canvas/spawn_children", {
        "project_id": project_id,
        "parent_node_id": parent_node_id,
        "children": children,
    }, timeout=30))


@mcp.tool()
def canvas_set_meta(project_id: str, patch_json: str) -> str:
    """🆕 v7 — 修改画布级 meta（自检 / 影视级模式 / 任何画布级开关）。

    Args:
        project_id: 项目 ID
        patch_json: JSON 字符串。常见 keys：
          - selfCheckEnabled (bool)
          - selfCheckMaxRetries (int 1-5)
          - selfCheckPassThreshold (int 5-10)
          - cinematicProMode (bool)
    """
    try:
        patch = json.loads(patch_json) if patch_json.strip() else {}
    except json.JSONDecodeError as e:
        return _dump({"ok": False, "error": f"patch_json 不是合法 JSON: {e}"})
    return _dump(_post_json("/canvas/set_meta", {
        "project_id": project_id,
        "patch": patch,
    }, timeout=10))


def main() -> None:
    import asyncio

    async def _run() -> None:
        await mcp.run_stdio_async()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()


# ─── v9 — image 魔法 / 多画布 / 表格批量 ─────────────────────────────


@mcp.tool()
def canvas_run_reverse_prompt(image_url: str, vision_model: str = "") -> str:
    """🆕 v9 — 反推图片为中文工业级 prompt（用于 prompt 复用 / 风格学习）。

    传入一张图（http URL 或 data:image base64），调诗云 vision 模型（默认 gpt-4o）
    输出 6 段中文 prompt + negative：
      ① 角色基础 ② 面部特写（≥5 lock 关键词）③ 发型与服饰
      ④ 场景与环境 ⑤ 光影与色调 ⑥ 镜头与构图（≥7 项）
      末尾 negative ≥7 项

    返回：{"prompt": "...", "modelUsed": "gpt-4o"}

    用法：拿到 prompt 后通常 spawn 一个 text 节点（kind="text", role="reverse-prompt"），
    或者直接给某个新 image / image2video 节点的 prompt 字段使用。

    Args:
        image_url: 图片 URL（http 或 data:image base64）
        vision_model: 可选指定 vision 模型（默认按 settings 选）
    """
    payload = {"image_url": image_url}
    if vision_model:
        payload["vision_model"] = vision_model
    return _dump(_post_json("/canvas/reverse_prompt", payload))


@mcp.tool()
def canvas_run_temporal(
    image_url: str, direction: str = "after", seconds: int = 3
) -> str:
    """🆕 v9 — 演绎画面：3 秒后 / 5 秒前。

    - direction="after"：用 image2video 跑 N 秒，抽末帧（最准但慢，约 240s）
    - direction="before"：用 image2image 反向 prompt（更快，约 30s）

    本工具是异步触发：发起请求后由前端画布执行并 spawn 一张子图节点。

    Args:
        image_url: 源图 URL
        direction: "after"（演绎到 N 秒后）或 "before"（回溯到 N 秒前）
        seconds: 时长（默认 3 秒，建议范围 1-15）
    """
    return _dump(
        _post_json(
            "/canvas/temporal",
            {"image_url": image_url, "direction": direction, "seconds": seconds},
        )
    )


@mcp.tool()
def canvas_create_subcanvas(project_id: str, name: str) -> str:
    """🆕 v9 — 在已有项目下新建一张画布（多画布 / 多集 / 多版本）。

    一个项目可以有 N 张画布。常见用法：
      - 短剧分集：main / ep1 / ep2 / ...
      - 多版本：cut-A / cut-B
      - 长片分幕：act1 / act2 / act3

    返回：新建的 canvas_id + 文件路径

    Args:
        project_id: 项目 ID
        name: 画布展示名（如"第二集" / "试拍版"）
    """
    return _dump(_post_json("/canvas/canvases/create", {"project_id": project_id, "name": name}))


@mcp.tool()
def canvas_list_subcanvases(project_id: str) -> str:
    """🆕 v9 — 列出项目内所有画布。

    返回：[{canvasId, name, relativePath, nodeCount, updatedAt}, ...]
    main 画布永远在第一位。

    Args:
        project_id: 项目 ID
    """
    return _dump(_post_json("/canvas/canvases/list", {"project_id": project_id}))


@mcp.tool()
def canvas_open_subcanvas(project_id: str, canvas_id: str) -> str:
    """🆕 v9 — 按 canvas_id 打开项目内某张画布（拿完整 nodes/edges/viewport）。

    Args:
        project_id: 项目 ID
        canvas_id: 画布 ID（"main" 或 "c_xxx"）
    """
    return _dump(_post_json("/canvas/canvases/open", {"project_id": project_id, "canvas_id": canvas_id}))


@mcp.tool()
def canvas_delete_subcanvas(project_id: str, canvas_id: str) -> str:
    """🆕 v9 — 删除项目内某张画布（不能删 main）。

    Args:
        project_id: 项目 ID
        canvas_id: 要删的 canvas_id（"c_xxx"，不是 "main"）
    """
    return _dump(_post_json("/canvas/canvases/delete", {"project_id": project_id, "canvas_id": canvas_id}))


@mcp.tool()
def canvas_rename_subcanvas(project_id: str, canvas_id: str, new_name: str) -> str:
    """🆕 v9 — 重命名项目内某张画布的展示名（不改 canvas_id 文件名）。

    Args:
        project_id: 项目 ID
        canvas_id: 要改名的 canvas_id
        new_name: 新展示名
    """
    return _dump(
        _post_json(
            "/canvas/canvases/rename",
            {"project_id": project_id, "canvas_id": canvas_id, "new_name": new_name},
        )
    )


# ─── v10 — 编导级专业能力 ────────────────────────────────────────


@mcp.tool()
def canvas_save_director_bible(
    project_id: str,
    look_profile: dict | None = None,
    audio_bible: dict | None = None,
) -> str:
    """🆕 v10 — 保存项目级"编导档案"（lookProfile + audioBible）。

    保存后，**该项目所有画布的所有 image / image2video 节点**
    跑的时候会**自动**把这两套档案注入 prompt 末尾，保证整片色彩 + 声音设计一致。

    look_profile 形如：
      {
        "name": "宋代古风冷青调",
        "colorTemperature": "cool",  # warm/neutral/cool/very-cool
        "dominantTones": "青灰偏冷，偶尔暖光点缀",
        "contrast": "medium",  # low/medium/high/very-high
        "keyLighting": "low-key 低调",
        "filmGrain": "film-grain-light",
        "notes": "..."
      }

    audio_bible 形如：
      {
        "themeMusicStyle": "古风弦乐 + 笛箫，悲悯",
        "characterMotif": "主角 motif：古琴单音重音 + 弦乐渐起",
        "ambientBaseline": "雨夜：雨声 + 远处更夫梆子 + 偶尔风吹竹叶",
        "foleyStyle": "极简，重要动作才出 Foley",
        "notes": "..."
      }

    Args:
        project_id: 项目 ID
        look_profile: 色彩档案 dict（可空）
        audio_bible: 声音档案 dict（可空）
    """
    payload: dict = {"project_id": project_id}
    if look_profile is not None:
        payload["look_profile"] = look_profile
    if audio_bible is not None:
        payload["audio_bible"] = audio_bible
    return _dump(_post_json("/canvas/director_bible/save", payload))


@mcp.tool()
def canvas_load_director_bible(project_id: str) -> str:
    """🆕 v10 — 读项目编导档案（lookProfile + audioBible）"""
    return _dump(_post_json("/canvas/director_bible/load", {"project_id": project_id}))


# ─── v11 — 剧本医生 + 音乐生成 ──────────────────────────────────────


@mcp.tool()
def canvas_run_script_doctor(
    scenes: list,
    user_intent: str = "",
    model: str = "",
) -> str:
    """🆕 v11 — 剧本医生：调 vision 模型按 6 维度评审剧本。

    维度：
      - hook（钩子）
      - characterArc（角色弧）
      - pacing（节奏）
      - dialogue（对白）
      - visualizability（视觉化）
      - emotionalImpact（情感张力）

    输出：6 维评分 + 整体评级 + 改进建议（critical/high/medium/low）+ 可选修订版 scenes

    Args:
        scenes: 剧本场景数组（来自 scriptGen.outputs.scenes）
        user_intent: 用户最初的意图（可选，提升评审准确性）
        model: 可选指定 chat 模型
    """
    payload: dict = {"scenes": scenes}
    if user_intent:
        payload["user_intent"] = user_intent
    if model:
        payload["model"] = model
    return _dump(_post_json("/canvas/script_doctor", payload))


@mcp.tool()
def canvas_run_music_gen(
    prompt: str = "",
    duration: int = 10,
    model: str = "audio1.0",
    timing_prompts: list | None = None,
) -> str:
    """🆕 v11 — 文生音效 / BGM / 卡点（vidu audio1.0 / kling-audio）。

    **v20 状态**：bagege 暂未挂 audio 变体；audio 业务**继续走诗云**。用户需在
    「设置 → 模型」把 audio_gen_base_url 配到诗云（shiyunapi.com）。

    两种模式：
      - 单段：prompt 描述 + duration（2-10s）→ 一段连续音频
      - 卡点：timing_prompts 数组（每段独立 from/to/prompt）→ 多段拼接

    用例：
      - 短剧 BGM：prompt="古风弦乐悲悯，10 秒环境氛围", duration=10
      - 卡点视频：timing_prompts=[
          {"from": 0, "to": 3, "prompt": "鸟鸣晨光"},
          {"from": 3, "to": 6, "prompt": "雨声渐起"},
          {"from": 5, "to": 9.5, "prompt": "海浪轻拍沙滩"}
        ]

    输出：audio_url（mp3）+ duration_seconds + model_used

    Args:
        prompt: 单段模式的描述
        duration: 时长（秒），2-10
        model: "audio1.0"（vidu）或 "kling-audio"（诗云 audio 渠道）
        timing_prompts: 卡点模式分段（list of {from, to, prompt}），传了就走 timing 模式
    """
    payload: dict = {
        "prompt": prompt,
        "duration": max(2, min(10, duration)),
        "model": model,
    }
    if timing_prompts:
        payload["timing_prompts"] = timing_prompts
    return _dump(_post_json("/canvas/music_gen", payload))


# ─── v13 — Prompt Optimizer ─────────────────────────────────────────


@mcp.tool()
def canvas_optimize_prompt(
    prompt: str,
    context: str = "",
    model: str = "",
) -> str:
    """🆕 v13 — Prompt 优化器（⭐ 一键扩写）。

    把用户的简短描述扩写成专业的 AI 图像/视频生成 prompt。
    包含：主体 + 动作 + 场景 + 光线 + 镜头 + 风格 + Negative。

    Args:
        prompt: 用户的简短描述（如"一个女孩在雨中跑"）
        context: 可选上下文（如"image 节点" / "image2video 节点"）
        model: 可选指定 chat 模型
    """
    payload: dict = {"prompt": prompt}
    if context:
        payload["context"] = context
    if model:
        payload["model"] = model
    return _dump(_post_json("/canvas/optimize_prompt", payload))



@mcp.tool()
def canvas_film_analysis(
    video_url: str,
    model: str = "",
) -> str:
    """🆕 v13 — 视频反推分镜表（Film Analysis）。

    上传任何视频 → AI 分析所有 shots / 运镜 / 角度 / 内容 → 输出结构化分镜表。
    每个 shot 包含可直接复用的中文 prompt（适合喂给 image2video）。

    工作原理：ffmpeg 每 2 秒抽一帧（最多 15 帧）→ 多图输入 vision 模型分析。

    输出：shots 数组（每个含 index/timecode/shot_size/camera_movement/angle/content/reusable_prompt）
         + total_duration_seconds + model_used

    用例：
      - 学习别人的镜头语言：上传参考视频 → 拿到分镜表 → 复用 prompt
      - 自己生成的视频 QC：分析是否符合预期的镜头规划

    Args:
        video_url: 视频 URL（https / file:// / data:）
        model: 可选指定 vision 模型
    """
    payload: dict = {"video_url": video_url}
    if model:
        payload["model"] = model
    return _dump(_post_json("/canvas/film_analysis", payload))



@mcp.tool()
def canvas_cutout(
    image_url: str,
) -> str:
    """🆕 v13 — 抠图（去除背景，输出透明 PNG）。

    优先用本地 rembg（需 pip install rembg），fallback 到 AI inpaint。
    输出存到 vault Canvas/_cutouts/。

    Args:
        image_url: 图片 URL（https / file:// / data:）
    """
    return _dump(_post_json("/canvas/cutout", {"image_url": image_url}))


@mcp.tool()
def canvas_outpaint(
    image_url: str,
    target_ratio: str = "21:9",
    prompt: str = "",
) -> str:
    """🆕 v13 — 扩图（Outpaint，扩展画面到目标比例）。

    保持原图内容不变，向四周扩展到目标比例。
    适用：16:9 → 21:9 宽银幕 / 1:1 → 16:9 横屏 等。

    Args:
        image_url: 原图 URL
        target_ratio: 目标比例（如 "21:9" / "16:9" / "9:16"）
        prompt: 可选扩展描述（如"延伸森林场景"）
    """
    payload: dict = {"image_url": image_url, "target_ratio": target_ratio}
    if prompt:
        payload["prompt"] = prompt
    return _dump(_post_json("/canvas/outpaint", payload))


@mcp.tool()
def canvas_compose_contact_sheet(
    image_urls: list,
    cols: int = 0,
) -> str:
    """🆕 v13 — 拼大图（Contact Sheet）：多张独立图 → 单张网格图。

    用途：把角色多视图拼成一张 pose sheet，作为单张 reference 传给 image2video。
    解决 Veo 3.1 / Seedance / Kling 只接 1-3 张 ref 的硬上限。

    Args:
        image_urls: 图片 URL 列表（3-9 张）
        cols: 列数（0=自动，按 √N 选）
    """
    payload: dict = {"image_urls": image_urls}
    if cols > 0:
        payload["cols"] = cols
    return _dump(_post_json("/canvas/compose_contact_sheet", payload))


@mcp.tool()
def canvas_generate_character_views(
    description: str,
    image_model: str,
    hero_url: str = "",
    aspect_ratio: str = "16:9",
) -> str:
    """🆕 v20 — 角色定妆 / 三视图 / 角色板生成。**调用前必须先问用户选哪条路径**（成本/质量/用途差很多）。

    ⚠️ 在生成角色图前，先在对话里问用户：
      ┌─────────────────────────────────────────────────────────┐
      │ 角色定妆有三条路，token 消耗、质量和用途不同，你选哪个？  │
      │ A）省钱快出：直接出一张三视图同框（正+侧+背）。           │
      │    一次调用搞定，但单张图里每个视角分辨率被摊薄，         │
      │    脸部细节相对糊。                                       │
      │ B）高质量（推荐）：先出一张正面脸部高清定妆照 → 你确认 →  │
      │    以它为参考扩出侧面/背面 → 拼成一张三视图。             │
      │    多花 2-3 次调用和配额，但每个视角都清晰、锁脸更稳。    │
      │ C）角色板 / 设计表：用专门的角色设计板提示词模板，         │
      │    一张图里包含身份、面部、服装材质、转视角、头部研究、   │
      │    表演/肢体语言和电影肖像。适合前期定风格、定服装、      │
      │    给导演/美术/后续镜头做综合 reference。                 │
      └─────────────────────────────────────────────────────────┘

    三种模式对应：

    A. **一锤子直出三视图同框**（`hero_url` 为空）
       直接生成 1 张含正面 / 侧面 / 背面的合成图。最快、最省，质量一般。

    B. **基于已有正面图扩三视图**（提供 `hero_url`）—— 用户选 B 时走这条：
       第 1 步：先用 canvas_add_node 加一张 image 节点，prompt 写「正面脸部
                高清定妆照」，跑出来贴给用户确认满意。
       第 2 步：拿那张正面图 URL 作 hero_url 调本工具，image2image 扩出
                侧面 + 背面（连同正面共 3 张返回）。
       第 3 步：canvas_compose_contact_sheet 把 3 张拼成单张三视图 pose sheet，
                喂下游 image2video.subjectRefs 锁脸。

    C. **角色板 / 电影级角色设计表**（不要调用本工具，改用 image 节点）
       用 canvas_add_node 新建 `image` 节点，prompt 使用“电影级角色设计表（一张直出）”
       模板，并把用户的角色设定填进去。最终画面必须是一张高预算动画提案板 /
       角色设计表，不是单张人物肖像、不是半身写真、不是纯人物海报。
       创建节点时 data.aspectRatio 必须固定为 "16:9"；角色板是横版 production board，
       不要沿用短剧竖屏 9:16 画幅。
       模板必须包含：
       - 角色身份：姓名 / 年龄 / 身高 / 体型 / 种族或设计语言
       - 面部：脸型骨骼 / 皮肤质感 / 眼睛 / 发型 / 疤痕或痣等识别点
       - 心理侧写与表演指导：核心特质 / 内在冲突 / 行为模式 / 微表情
       - 肢体语言与服装材质：姿势倾向 / 动作节奏 / 面料磨损 / 配饰道具
       - 转视角：全身正面 / 3/4 侧 / 侧面 / 背面 / 3/4 背面，比例服装一致
       - 头部研究：正面中性 / 3/4 个性 / 侧面结构 / 低头 / 抬头 / 动态角度
       - 电影肖像：只作为角色板里的一个小分区，包含环境 / 灯光 / 色调 /
         叙事表情，50mm 或 85mm 浅景深；不要让电影肖像变成整张图主体
       - 输出：身高比例尺、标注说明、生产笔记、多视角全身转面、头部研究、
         材质细节块、表演备注块，制作就绪，无水印
       - 负面约束：严禁输出单个站立人物照片、单人半身照、普通城市肖像、
         只有一个人物占满画面
       这条路不是单纯锁脸三视图，而是“角色设计总 reference”。后续可把这张图
       存为人物主体，或作为 image.reference / image2video.subjectRefs 的综合参考。

    Args:
        description: 角色 Bible 全文（≥200 字含 8 维 identity lock + 标志物 + negative）
        image_model: 图像模型 ID（v20 bagege 推荐 `bggai-nano-banana-pro-text-to-image-v1`
                     或 `bggai-nano-banana-pro-image-to-image-v1`；廉价档 `bs-gpt-image-2`）
        hero_url: 已有正面图 URL（可空 → 走模式 A；填了 → 走模式 B 扩视图）
        aspect_ratio: 输出比例（默认 16:9）

    返回：{"views": [{"angle": "正面/侧面/背面" 或 "三视图同框", "url": "..."}]}
    """
    payload: dict = {
        "description": description,
        "image_model": image_model,
        "aspect_ratio": aspect_ratio,
    }
    if hero_url:
        payload["hero_url"] = hero_url
    return _dump(_post_json("/canvas/generate_character_views", payload, timeout=300))


@mcp.tool()
def canvas_split_grid(
    image_url: str,
    rows: int,
    cols: int,
) -> str:
    """遗留工具 — 网格图片几何切割（非标准故事板流程）。

    ⚠️ 不要把它当成 Hermes 视频画布的默认路径。
    标准流程是：角色卡/角色设计板 → 场景/道具 → Shot Table 镜头表 →
    选择生产方案 → 参考图连线 / 镜头视觉锚点 → image2video → videoConcat。

    仅在用户已经明确提供一张现成的多宫格图片，并要求“把这张图切开”时使用。
    它只做像素裁切，不理解镜头、不生成 Shot Table、不保证角色或服装一致性。
    Hermes 不应主动生成网格故事板再切图来做视频。

    Args:
        image_url: 待切割图片 URL（https / data: / vault 相对路径）
        rows: 网格行数（1-6，如 3×2 图片填 rows=2）
        cols: 网格列数（1-6，如 3×2 图片填 cols=3）

    返回：{"panels": [{"url": "...", "index": 1, "row": 1, "col": 1}, ...]}
          panels 按从上到下、从左到右排序，url 是 vault 相对路径
    """
    return _dump(_post_json("/canvas/split_grid", {
        "image_url": image_url,
        "rows": int(rows),
        "cols": int(cols),
    }, timeout=120))
