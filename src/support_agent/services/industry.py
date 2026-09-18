"""光伏行业的实体识别与片段元数据。

普通 RAG 只按文本相似度排序，在这个领域会出问题：同一份语料里同时存在
不同版本、不同机型、不同场景的说法，语义相近但现场结论可能相反。
「SUN2000 2.2 的某寄存器倍率」和「SUN2000 3.0 的同一寄存器倍率」文字很像，
把它们混在一起给出的答案看着合理、拿到现场却是错的。

所以在切分阶段就给每个片段贴上行业标签（`manufacturer` / `device_models` /
`protocols` / `document_version` / `scenario` / `content_type`），检索时先看标签，
再比相似度。

两条克制原则：

1. **只抽确定性可判的**。标签全部由词典和正则命中得出，不做任何猜测。
   抽不到就是空，不写「可能是 SUN2000」这种模糊值——元数据一旦不可信，
   拿它做过滤比不做过滤更危险。
2. **抽取只发生在导入时一次**，不放在检索路径上，避免每次问答都重算。
   检索侧只需要从**用户问题**里抽同一批实体（`query_facets`）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# 设备机型
# ---------------------------------------------------------------------------

# 系列名。片段级检索用系列就够；具体型号留给后续的结构化点表场景。
DEVICE_SERIES: tuple[str, ...] = (
    "SUN2000",
    "SUN5000",
    "LUNA2000",
    "SmartLogger",
    "SDongle",
    "EMMA",
    "iCleanLogger",
    "HAV1",
    "HAV2",
    "HAV3",
    "HAV5",
)

# 带前缀的完整型号，例如 SUN2000-100KTL-M1、LUNA2000-215。
# 语料里还有「100/110/115KTL-M2」这种省略前缀的写法，无法确定归属，不抽。
DEVICE_MODEL_PATTERN = re.compile(
    r"\b(?:SUN2000|SUN5000|LUNA2000)-[0-9][0-9A-Za-z/\-()~.,]*",
)

# ---------------------------------------------------------------------------
# 通信协议
# ---------------------------------------------------------------------------

# 顺序即优先级：具体的写在笼统的前面，这样「Modbus TCP」先被吃掉，
# 剩下的「Modbus」才是真正没写变体的裸 Modbus。
PROTOCOL_PATTERNS: tuple[tuple[str, str], ...] = (
    ("IEC 104", r"IEC\s*(?:60870-5-)?104"),
    ("IEC 103", r"IEC\s*(?:60870-5-)?103"),
    ("IEC 61850", r"IEC\s*61850"),
    ("Modbus TCP", r"Modbus\s*[\/\-]?\s*TCP"),
    ("Modbus RTU", r"Modbus\s*[\/\-]?\s*RTU"),
    ("Modbus", r"Modbus"),
    ("MBUS", r"MBUS"),
    ("RS485", r"RS\s*[\-_]?\s*485"),
    ("DL/T 645", r"DL\s*/\s*T\s*645"),
    ("MQTT", r"MQTT"),
    ("4G LTE", r"4G\s*LTE"),
)

# ---------------------------------------------------------------------------
# 文档版本与场景
# ---------------------------------------------------------------------------

# 「V2.0」「v1.3.2」这类版本号；前面不能再接字母数字，避免把型号里的片段当版本。
VERSION_PATTERN = re.compile(r"(?<![A-Za-z0-9])[Vv](\d+(?:\.\d+)*)(?![0-9])")
# 拓展资料按分册命名，例如「第3册 交直流屏柜原理」。
VOLUME_PATTERN = re.compile(r"第\s*(\d+)\s*册")

# document_id 前缀 → 场景。语料的十四册和附录在这里定场景归属。
SCENARIO_BY_DOCUMENT: dict[str, str] = {
    "M1": "通用基础",
    "M2": "户用",
    "M3": "工商业储能",
    "M4": "工商业",
    "M5": "工商业",
    "M6": "工商业",
    "M7": "地面电站",
    "M8": "地面电站",
    "M9": "地面电站",
    "M10": "管理系统",
    "M11": "EHS",
    "M12": "客服",
    "M13": "物流",
    "M14": "工程质量",
    "V3": "交直流屏柜",
}
APPENDIX_SCENARIO = "跨模块速查"

# 章节标题 → 片段类型。取第一个命中的关键词，顺序即优先级。
CONTENT_TYPE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("register_table", ("点表", "寄存器", "寄存器地址", "点位")),
    ("faq", ("FAQ", "常见问题", "问题→", "问题 ->")),
    ("reference", ("速查", "索引", "总表", "术语", "缩略语", "汇总", "总纲")),
    ("procedure", ("安装", "调测", "维护", "指导", "调试", "配置", "开局")),
    ("spec", ("规格", "参数", "容量", "选型")),
)
DEFAULT_CONTENT_TYPE = "manual"

MANUFACTURER_BY_DOCUMENT_PREFIX = "Huawei"


# ---------------------------------------------------------------------------
# 抽取
# ---------------------------------------------------------------------------


def extract_device_models(text: str) -> list[str]:
    """抽出片段里出现过的机型；完整型号和系列名都收，按出现顺序去重。

    系列名一律补上，哪怕片段里写的是完整型号：用户平时按系列提问
    （「SUN2000 通信参数在哪配」），只存 `SUN2000-100KTL-M1` 这类完整型号，
    集合求交时和「SUN2000」对不上，行业加权就形同虚设。
    """
    found: list[str] = []
    remaining = text
    for match in DEVICE_MODEL_PATTERN.finditer(text):
        model = match.group(0).strip(" ,.、）)").upper()
        if model and model not in found:
            found.append(model)
    for series in DEVICE_SERIES:
        if series.upper() in remaining.upper() and series.upper() not in found:
            found.append(series)
    return found


def extract_protocols(text: str) -> list[str]:
    """抽出片段里提到的通信协议，按具体到笼统的顺序匹配，长模式先占位。"""
    remaining = text
    found: list[str] = []
    for canonical, pattern in PROTOCOL_PATTERNS:
        if re.search(pattern, remaining, flags=re.IGNORECASE):
            found.append(canonical)
            # 匹配过的部分挖掉，避免「Modbus TCP」之后又被裸 Modbus 再算一次。
            remaining = re.sub(pattern, " ", remaining, flags=re.IGNORECASE)
    return found


def extract_document_version(*texts: str) -> str | None:
    """从文档标题、文件名里判断版本号；分册资料退化成「第N册」。"""
    for text in texts:
        if not text:
            continue
        match = VERSION_PATTERN.search(text)
        if match:
            return f"V{match.group(1)}"
    for text in texts:
        if not text:
            continue
        match = VOLUME_PATTERN.search(text)
        if match:
            return f"第{match.group(1)}册"
    return None


def scenario_for_document(document_id: str) -> str:
    """按语料编号判断所属场景；附录归入跨模块速查。"""
    key = document_id.strip().upper()
    if key in SCENARIO_BY_DOCUMENT:
        return SCENARIO_BY_DOCUMENT[key]
    if key.startswith("M") and key[1:].isdigit():
        return "通用"
    return APPENDIX_SCENARIO


def classify_content_type(section_title: str, document_title: str = "") -> str:
    """按标题关键词判断片段类型；判断不出来就是普通手册章节。"""
    haystack = f"{section_title} {document_title}"
    for content_type, keywords in CONTENT_TYPE_RULES:
        if any(keyword in haystack for keyword in keywords):
            return content_type
    return DEFAULT_CONTENT_TYPE


def manufacturer_for_document(document_id: str) -> str | None:
    """这批语料来自华为培训教材；其他来源的资料标为空。"""
    key = document_id.strip().upper()
    if key.startswith("M") and key[1:].isdigit():
        return MANUFACTURER_BY_DOCUMENT_PREFIX
    if key in {"A", "B", "C", "D", "E"}:
        return MANUFACTURER_BY_DOCUMENT_PREFIX
    return None


# ---------------------------------------------------------------------------
# 面向检索的封装
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndustryFacets:
    """一次查询里出现的行业实体，用来给检索结果加权。"""

    device_models: tuple[str, ...] = ()
    protocols: tuple[str, ...] = ()
    document_version: str | None = None
    scenario: str | None = None

    @property
    def empty(self) -> bool:
        return not (self.device_models or self.protocols or self.document_version or self.scenario)

    def as_text(self) -> str:
        """拼成一行，用于在日志和审计里说明这次按什么加权。"""
        parts = []
        if self.device_models:
            parts.append("机型=" + "/".join(self.device_models))
        if self.protocols:
            parts.append("协议=" + "/".join(self.protocols))
        if self.document_version:
            parts.append(f"版本={self.document_version}")
        if self.scenario:
            parts.append(f"场景={self.scenario}")
        return " ".join(parts)


# 场景词：用户提到这些词时，优先该场景的资料。
SCENARIO_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("户用", "户用"),
    ("家庭", "户用"),
    ("工商业", "工商业"),
    ("地面电站", "地面电站"),
    ("大型电站", "地面电站"),
    ("储能", "工商业储能"),
    ("交直流屏", "交直流屏柜"),
    ("合母", "交直流屏柜"),
    ("控母", "交直流屏柜"),
)


def query_facets(text: str) -> IndustryFacets:
    """从**用户问题**里抽行业实体。

    只抽问题里明确写出来的东西：用户问「户用」才按户用加权，
    没写就说明他不限定，这时任何加权都是在替他做决定。
    """
    scenarios: list[str] = []
    for keyword, scenario in SCENARIO_KEYWORDS:
        if keyword in text and scenario not in scenarios:
            scenarios.append(scenario)
    return IndustryFacets(
        device_models=tuple(extract_device_models(text)),
        protocols=tuple(extract_protocols(text)),
        document_version=extract_document_version(text),
        scenario=scenarios[0] if scenarios else None,
    )


def build_chunk_metadata(
    *,
    document_id: str,
    document_title: str,
    section_title: str,
    source_file: str,
    corpus_id: str,
    content: str = "",
    extra: dict[str, Any] | None = None,
    document_version: str | None = None,
) -> dict[str, Any]:
    """汇总一个片段的行业标签。

    型号和协议签在**正文**上：光伏资料的小节标题通常只写「6.2 绝缘阻抗定位」，
    真正提到 RS485、Modbus TCP、SUN2000 的是正文。只扫标题会几乎全部抽空
    （实测 95 个章节只命中 4 个机型、0 个协议），元数据就没用了。

    片段类型只按**标题**判：正文里任何词都可能偶然出现，
    用正文判类型会把「安装指导」误标成「点表」。

    抽不到的字段留空列表或 None，不写默认值——元数据一旦不可信，
    拿它做排序比不做排序更危险。
    """
    body = f"{section_title}\n{document_title}\n{content}"
    metadata: dict[str, Any] = {
        "document_id": document_id,
        "document_title": document_title,
        "section_title": section_title,
        "source_file": source_file,
        "corpus_id": corpus_id,
        "manufacturer": manufacturer_for_document(document_id),
        "device_models": extract_device_models(body),
        "protocols": extract_protocols(body),
        "document_version": document_version
        or extract_document_version(document_title, source_file),
        "scenario": scenario_for_document(document_id),
        "content_type": classify_content_type(section_title, document_title),
    }
    if extra:
        metadata.update(extra)
    return metadata


# 机型超过这个数量就归纳成「N 个机型通用」，不再逐个罗列。
# 语料里有片段一次列了十几个型号，那在语义上就是「跨机型通用条款」；
# 全量拼进标签后，模型会把这一长串连同正文一起抄进回答，糊满一屏却没有
# 任何区分度。真正有信息量的是「这段只适用某几个机型」的情况。
MODEL_LIST_LIMIT = 3


def _describe_models(models: Any) -> str:
    """机型少就列出来（那是有区分度的信息），多则只报数量。"""
    names = [str(item) for item in models]
    if len(names) <= MODEL_LIST_LIMIT:
        return "/".join(names)
    return f"{len(names)} 个机型通用"


def describe_facets(metadata: dict[str, Any]) -> str:
    """把片段标签压成一行，附在检索结果里给模型看。

    模型需要知道「这条依据出自哪个版本、哪个机型」，否则它只能把两份
    说法不同的资料揉成一个答案——而现场恰恰最怕这个。

    这行标签会被模型抄进回答，所以必须够短：版本和场景是关键信息，
    机型列表过长时只报数量（见 ``MODEL_LIST_LIMIT``）。
    """
    parts: list[str] = []
    version = metadata.get("document_version")
    if version:
        parts.append(str(version))
    scenario = metadata.get("scenario")
    if scenario:
        parts.append(str(scenario))
    if metadata.get("protocols"):
        parts.append("/".join(metadata["protocols"]))
    if metadata.get("device_models"):
        parts.append(_describe_models(metadata["device_models"]))
    content_type = metadata.get("content_type")
    if content_type and content_type != DEFAULT_CONTENT_TYPE:
        parts.append(str(content_type))
    return " · ".join(parts)


@dataclass
class MetadataSearchSignals:
    """元数据加权算出来的两个集合，供检索打分使用。

    分成「匹配」和「冲突」而不是「保留/丢弃」：语料对机型版本的覆盖并不完整，
    硬过滤会把「跨机型通用」的章节一起杀掉，反而让模型拿不到任何依据。
    所以这里只做加分和降权，最终是否采用仍由分数决定。
    """

    matched: list[str] = field(default_factory=list)
    conflicted: list[str] = field(default_factory=list)


def metadata_signals(facets: IndustryFacets, metadata: dict[str, Any]) -> MetadataSearchSignals:
    """比较查询实体与片段标签，得出加分项和降权项。"""
    signals = MetadataSearchSignals()
    if facets.device_models:
        chunk_models = {str(item).upper() for item in metadata.get("device_models") or []}
        query_models = {item.upper() for item in facets.device_models}
        if chunk_models & query_models:
            signals.matched.append("机型")
        elif chunk_models:
            # 片段明确属于别的机型，且没有一个对得上。
            signals.conflicted.append("机型")
    if facets.protocols:
        chunk_protocols = {str(item) for item in metadata.get("protocols") or []}
        if chunk_protocols & set(facets.protocols):
            signals.matched.append("协议")
        elif chunk_protocols:
            signals.conflicted.append("协议")
    if facets.scenario:
        scenario = metadata.get("scenario")
        if scenario == facets.scenario:
            signals.matched.append("场景")
        elif scenario and scenario in {"户用", "工商业", "工商业储能", "地面电站"}:
            # 只在具体场景之间互相排斥；通用章节和跨模块速查不降权。
            signals.conflicted.append("场景")
    return signals
