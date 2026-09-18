"""行业元数据抽取的单元测试。

这些断言全部对着**真实资料的写法**写：机型、协议、版本号都取自 HCSA 分卷
和拓展资料里实际出现过的字符串，不用编造的样例，否则测试通过也说明不了
元数据在真实语料上抽得出来。
"""

from support_agent.services.industry import (
    IndustryFacets,
    build_chunk_metadata,
    classify_content_type,
    describe_facets,
    extract_device_models,
    extract_document_version,
    extract_protocols,
    metadata_signals,
    query_facets,
    scenario_for_document,
)


def test_protocols_prefer_longest_match() -> None:
    """「Modbus TCP」必须整体被吃掉，不能再被裸 Modbus 重复算一次。"""
    text = "支持 Modbus TCP 与 Modbus-RTU，调度侧走 IEC 60870-5-104，箱变走 IEC 103。"
    assert extract_protocols(text) == ["IEC 104", "IEC 103", "Modbus TCP", "Modbus RTU"]


def test_protocols_returns_empty_when_nothing_matched() -> None:
    """抽不到就是空列表；不写「未知协议」这类占位值让检索误判。"""
    assert extract_protocols("逆变器把直流电转成交流电。") == []


def test_device_models_keep_series_and_full_model() -> None:
    """系列名和完整型号都要收：用户按「SUN2000」提问时得能对上完整型号的片段。"""
    models = extract_device_models("SUN2000-100KTL-M1 与 LUNA2000-215 组成光储系统。")
    assert "SUN2000-100KTL-M1" in models
    assert "SUN2000" in models
    assert "LUNA2000" in models


def test_document_version_from_title_and_volume() -> None:
    assert extract_document_version("HCSA-Field-Smart PV V2.0 培训教材.pdf") == "V2.0"
    assert extract_document_version("第3册 交直流屏柜原理（结合图纸扩充版）") == "第3册"
    assert extract_document_version("无版本的普通文档") is None


def test_document_version_does_not_read_model_number_as_version() -> None:
    """型号里的 `KTL` 后面跟的数字不是版本号，别把 V 前缀规则用错地方。"""
    assert extract_document_version("SUN2000-100KTL-M1 安装指导") is None


def test_scenario_and_content_type() -> None:
    assert scenario_for_document("M2") == "户用"
    assert scenario_for_document("M7") == "地面电站"
    assert scenario_for_document("A") == "跨模块速查"
    assert classify_content_type("A2 · 机型索引 ★★") == "reference"
    assert classify_content_type("E2 · 给 Agent 的检索建议") == "manual"
    assert classify_content_type("附录 C · 跨模块 FAQ（问题 → 定位）") == "faq"
    # 语料里「维护」写在文档标题上，不在小节标题里，所以要一起送进去判。
    assert (
        classify_content_type("6.1 升级与日志", "工商业解决方案维护指导（纯光场景）") == "procedure"
    )
    assert classify_content_type("2.9 调测与建站 ★★") == "procedure"
    # 判不出来就是普通手册章节，不硬塞一个类型。
    assert classify_content_type("1.7 逆变器分类与结构") == "manual"


def test_build_chunk_metadata_reads_protocols_from_body() -> None:
    """协议和机型在正文里，只扫标题会几乎全抽空。"""
    metadata = build_chunk_metadata(
        document_id="M3",
        document_title="智能光伏工商业储能 N+1 交付指导",
        section_title="3.4 通信组网",
        source_file="M3-智能光伏工商业储能N+1交付指导.md",
        corpus_id="smartpv_v2",
        content="储能柜通过 RS485 级联，SmartLogger 与逆变器之间使用 Modbus TCP。",
        document_version="V1.0",
    )
    assert metadata["protocols"] == ["Modbus TCP", "RS485"]
    assert "SmartLogger" in metadata["device_models"]
    assert metadata["document_version"] == "V1.0"
    assert metadata["scenario"] == "工商业储能"
    assert metadata["manufacturer"] == "Huawei"


def test_metadata_signals_match_and_conflict() -> None:
    """询问机型时：同型号加分，明确别的型号降权，没写机型的不参与。"""
    facets = IndustryFacets(device_models=("SUN2000",), scenario="户用")
    matched = metadata_signals(
        facets, {"device_models": ["SUN2000-100KTL-M1", "SUN2000"], "scenario": "户用"}
    )
    assert "机型" in matched.matched and "场景" in matched.matched
    assert matched.conflicted == []

    conflicted = metadata_signals(facets, {"device_models": ["LUNA2000"], "scenario": "地面电站"})
    assert conflicted.matched == []
    assert set(conflicted.conflicted) == {"机型", "场景"}

    neutral = metadata_signals(facets, {"device_models": [], "scenario": "跨模块速查"})
    assert neutral.matched == [] and neutral.conflicted == []


def test_query_facets_only_picks_explicit_entities() -> None:
    """用户没写机型就不猜：没写说明他不限定，替他把范围收窄是自作主张。"""
    facets = query_facets("啥是合母")
    assert facets.device_models == ()
    assert facets.scenario == "交直流屏柜"

    facets = query_facets("SUN2000 通过 Modbus TCP 怎么接")
    assert "SUN2000" in facets.device_models
    assert facets.protocols == ("Modbus TCP",)


def test_describe_facets_summarises_long_model_lists() -> None:
    """这行标签会被模型抄进回答，所以机型多到一定数量就只报数量。

    真实语料里存在一次列了 14 个型号的片段，那在语义上是「跨机型通用条款」；
    逐个罗列只会让回答糊满一屏型号名，却没有任何区分度。少数几个机型则相反，
    那正是「这段只适用这几款」的关键信息，必须保留。
    """
    few = describe_facets(
        {
            "document_version": "V2.0",
            "scenario": "工商业",
            "device_models": ["SUN2000-100KTL-M1", "LUNA2000"],
        }
    )
    assert few == "V2.0 · 工商业 · SUN2000-100KTL-M1/LUNA2000"

    many = describe_facets(
        {
            "document_version": "V2.0",
            "scenario": "户用",
            "device_models": [f"SUN2000-{index}KTL" for index in range(14)],
        }
    )
    assert many == "V2.0 · 户用 · 14 个机型通用"
    assert "SUN2000-13KTL" not in many
