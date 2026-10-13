import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple


def _fallback_result(comment: str = "评分服务暂时不可用") -> Dict[str, Any]:
    return {
        "score": None,
        "overall_comment": comment,
        "problems": [],
        "suggestions": [],
    }


def _get_doubao_config() -> Dict[str, Any]:
    return {
        "api_key": os.getenv("DOUBAO_API_KEY", "").strip(),
        "model": os.getenv("DOUBAO_MODEL", "").strip(),
        "base_url": os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").strip(),
        "timeout": float(os.getenv("DOUBAO_TIMEOUT", "40")),
    }


def _chat_completions_url(base_url: str) -> str:
    base = (base_url or "").rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _build_messages_squat(analysis: Dict[str, Any]) -> Tuple[str, str]:
    system_prompt = (
        "你是专业的动作评估助手。"
        "你只做深蹲(squat)评分解释。"
        "必须输出严格JSON，不要输出Markdown，不要输出额外文本。"
        "输出字段固定为: score, overall_comment, problems, suggestions。"
        "其中 score 为0-100整数；problems和suggestions各输出0-3条简短中文句子。"
    )
    user_payload = {
        "action_type": "squat",
        "angles": analysis.get("angles", {}),
        "symmetry": analysis.get("symmetry", {}),
        "validity": analysis.get("validity", {}),
        "confidence_summary": analysis.get("confidence_summary", {}),
    }
    user_prompt = (
        "请基于以下结构化姿态分析结果，输出深蹲评分JSON。\n"
        "重点关注：下蹲深度、膝髋协同、左右对称性、躯干稳定性。\n"
        "若 validity.enough_keypoints=false，必须返回无法可靠评分："
        '{"score": null, "overall_comment": "当前图片无法可靠评分", "problems": [], "suggestions": []}\n'
        "除上述字段外不要输出任何其他字段。\n"
        f"输入数据: {json.dumps(user_payload, ensure_ascii=False)}"
    )
    return system_prompt, user_prompt


def _build_messages_plank(analysis: Dict[str, Any]) -> Tuple[str, str]:
    system_prompt = (
        "你是专业的动作评估助手。"
        "你只做平板支撑(plank)评分解释。"
        "必须输出严格JSON，不要输出Markdown，不要输出额外文本。"
        "输出字段固定为: score, overall_comment, problems, suggestions。"
        "其中 score 为0-100整数；problems和suggestions各输出0-3条简短中文句子。"
    )
    user_payload = {
        "action_type": "plank",
        "angles": analysis.get("angles", {}),
        "alignment": analysis.get("alignment", {}),
        "validity": analysis.get("validity", {}),
        "confidence_summary": analysis.get("confidence_summary", {}),
    }
    user_prompt = (
        "请基于以下结构化姿态分析结果，输出平板支撑评分JSON。\n"
        "重点关注：身体是否平直、髋部过高或过低、躯干稳定性、整体姿态是否接近平板标准形态。\n"
        "若 validity.enough_keypoints=false，必须返回无法可靠评分："
        '{"score": null, "overall_comment": "当前图片无法可靠评分", "problems": [], "suggestions": []}\n'
        "除上述字段外不要输出任何其他字段。\n"
        f"输入数据: {json.dumps(user_payload, ensure_ascii=False)}"
    )
    return system_prompt, user_prompt


def _build_messages_pushup(analysis: Dict[str, Any]) -> Tuple[str, str]:
    system_prompt = (
        "你是专业的动作评估助手。"
        "你只做俯卧撑(pushup)评分解释。"
        "必须输出严格JSON，不要输出Markdown，不要输出额外文本。"
        "输出字段固定为: score, overall_comment, problems, suggestions。"
        "其中 score 为0-100整数；problems和suggestions各输出0-3条简短中文句子。"
    )
    user_payload = {
        "action_type": "pushup",
        "angles": analysis.get("angles", {}),
        "alignment": analysis.get("alignment", {}),
        "symmetry": analysis.get("symmetry", {}),
        "validity": analysis.get("validity", {}),
        "confidence_summary": analysis.get("confidence_summary", {}),
    }
    user_prompt = (
        "请基于以下结构化姿态分析结果，输出俯卧撑评分JSON。\n"
        "重点关注：肘部弯曲幅度、左右手臂对称性、身体从肩到踝是否保持直线、髋部是否塌腰或撅臀。\n"
        "若 validity.enough_keypoints=false，必须返回无法可靠评分："
        '{"score": null, "overall_comment": "当前图片无法可靠评分", "problems": [], "suggestions": []}\n'
        "除上述字段外不要输出任何其他字段。\n"
        f"输入数据: {json.dumps(user_payload, ensure_ascii=False)}"
    )
    return system_prompt, user_prompt


def _build_messages_glute_bridge(analysis: Dict[str, Any]) -> Tuple[str, str]:
    system_prompt = (
        "你是专业的动作评估助手。"
        "你只做臀桥(glute_bridge)评分解释。"
        "必须输出严格JSON，不要输出Markdown，不要输出额外文本。"
        "输出字段固定为: score, overall_comment, problems, suggestions。"
        "其中 score 为0-100整数；problems和suggestions各输出0-3条简短中文句子。"
    )
    user_payload = {
        "action_type": "glute_bridge",
        "angles": analysis.get("angles", {}),
        "alignment": analysis.get("alignment", {}),
        "symmetry": analysis.get("symmetry", {}),
        "validity": analysis.get("validity", {}),
        "confidence_summary": analysis.get("confidence_summary", {}),
    }
    user_prompt = (
        "请基于以下结构化姿态分析结果，输出臀桥评分JSON。\n"
        "重点关注：髋部是否充分伸展、肩-髋-膝是否接近一条直线、膝角是否稳定、左右髋膝是否对称。\n"
        "若 validity.enough_keypoints=false，必须返回无法可靠评分："
        '{"score": null, "overall_comment": "当前图片无法可靠评分", "problems": [], "suggestions": []}\n'
        "除上述字段外不要输出任何其他字段。\n"
        f"输入数据: {json.dumps(user_payload, ensure_ascii=False)}"
    )
    return system_prompt, user_prompt


def _build_messages_situp(analysis: Dict[str, Any]) -> Tuple[str, str]:
    system_prompt = (
        "你是专业的动作评估助手。"
        "你只做仰卧起坐(situp)评分解释。"
        "必须输出严格JSON，不要输出Markdown，不要输出额外文本。"
        "输出字段固定为: score, overall_comment, problems, suggestions。"
        "其中 score 为0-100整数；problems和suggestions各输出0-3条简短中文句子。"
    )
    user_payload = {
        "action_type": "situp",
        "angles": analysis.get("angles", {}),
        "alignment": analysis.get("alignment", {}),
        "symmetry": analysis.get("symmetry", {}),
        "validity": analysis.get("validity", {}),
        "confidence_summary": analysis.get("confidence_summary", {}),
    }
    user_prompt = (
        "请基于以下结构化姿态分析结果，输出仰卧起坐评分JSON。\n"
        "重点关注：躯干抬起幅度、髋屈曲角、膝部稳定性、左右髋膝是否对称、动作是否完整。\n"
        "若 validity.enough_keypoints=false，必须返回无法可靠评分："
        '{"score": null, "overall_comment": "当前图片无法可靠评分", "problems": [], "suggestions": []}\n'
        "除上述字段外不要输出任何其他字段。\n"
        f"输入数据: {json.dumps(user_payload, ensure_ascii=False)}"
    )
    return system_prompt, user_prompt


def _extract_text_content(api_resp: Dict[str, Any]) -> str:
    try:
        content = api_resp["choices"][0]["message"]["content"]
        if isinstance(content, list):
            # Compatible with some multimodal style outputs.
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            return "\n".join(parts).strip()
        return str(content).strip()
    except Exception:
        return ""


def _parse_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    # 1) direct JSON
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # 2) fenced code block JSON
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        try:
            obj = json.loads(fenced.group(1))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

    # 3) first object-like substring
    lo = text.find("{")
    hi = text.rfind("}")
    if lo >= 0 and hi > lo:
        try:
            obj = json.loads(text[lo : hi + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            return None
    return None


def _normalize_score_result(data: Dict[str, Any]) -> Dict[str, Any]:
    score = data.get("score")
    if score is not None:
        try:
            score = int(round(float(score)))
            score = max(0, min(100, score))
        except Exception:
            score = None

    overall_comment = str(data.get("overall_comment") or "").strip()
    if not overall_comment:
        overall_comment = "评分结果已生成"
    if len(overall_comment) > 80:
        overall_comment = overall_comment[:80].rstrip() + "..."

    def _norm_list(v: Any) -> list:
        if not isinstance(v, list):
            return []
        out = []
        for x in v:
            s = str(x).strip()
            if s:
                out.append(s)
        return out[:3]

    return {
        "score": score,
        "overall_comment": overall_comment,
        "problems": _norm_list(data.get("problems")),
        "suggestions": _norm_list(data.get("suggestions")),
    }


def _post_chat(payload: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        _chat_completions_url(cfg["base_url"]),
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=cfg["timeout"]) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            return json.loads(raw), None
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="ignore")
        except Exception:
            detail = str(e)
        return None, f"http_{e.code}:{detail}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def score_pose_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    validity = (analysis or {}).get("validity") or {}
    if not validity.get("enough_keypoints", False):
        return {
            "score": None,
            "overall_comment": f"当前图片无法可靠评分：{validity.get('reason') or '关键点不足'}",
            "problems": [],
            "suggestions": [],
        }

    cfg = _get_doubao_config()
    if not cfg["api_key"] or not cfg["model"]:
        return _fallback_result("评分服务暂未配置")

    action_type = str((analysis or {}).get("action_type") or "squat").strip().lower()
    if action_type == "plank":
        system_prompt, user_prompt = _build_messages_plank(analysis)
    elif action_type == "pushup":
        system_prompt, user_prompt = _build_messages_pushup(analysis)
    elif action_type == "glute_bridge":
        system_prompt, user_prompt = _build_messages_glute_bridge(analysis)
    elif action_type == "situp":
        system_prompt, user_prompt = _build_messages_situp(analysis)
    else:
        system_prompt, user_prompt = _build_messages_squat(analysis)
    payload = {
        "model": cfg["model"],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    api_data, err = _post_chat(payload, cfg)
    if api_data is None and err:
        # Some Doubao models don't support response_format=json_object.
        if "json_object" in err and "not supported" in err:
            payload.pop("response_format", None)
            api_data, err = _post_chat(payload, cfg)
        if api_data is None:
            return _fallback_result("评分服务暂时不可用")

    text = _extract_text_content(api_data)
    parsed = _parse_json_from_text(text)
    if not parsed:
        return _fallback_result("评分结果解析失败")
    return _normalize_score_result(parsed)


def score_squat_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(analysis or {})
    a["action_type"] = "squat"
    return score_pose_with_doubao(a)


def score_plank_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(analysis or {})
    a["action_type"] = "plank"
    return score_pose_with_doubao(a)


def score_pushup_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(analysis or {})
    a["action_type"] = "pushup"
    return score_pose_with_doubao(a)


def score_glute_bridge_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(analysis or {})
    a["action_type"] = "glute_bridge"
    return score_pose_with_doubao(a)


def score_situp_with_doubao(analysis: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(analysis or {})
    a["action_type"] = "situp"
    return score_pose_with_doubao(a)
