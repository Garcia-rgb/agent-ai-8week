from support_agent.services.embeddings import (
    bigram_terms,
    retrieval_terms,
    strip_stopwords,
    tokenize,
)


def test_strip_stopwords_keeps_domain_terms() -> None:
    # 口语问句剥掉虚词和语气词后，只剩承载信息的实词。
    assert strip_stopwords("啥是控母") == "控母"
    assert strip_stopwords("合母是啥意思啊") == "合母"
    # 领域术语里的字不能被当成虚词误删。
    assert "合" in strip_stopwords("合母")
    assert "母" in strip_stopwords("合母")


def test_retrieval_terms_separate_compound_terms() -> None:
    # 「合母」和「控母」共享「母」，逐字切分区分不开，两字组合后各自独立。
    assert retrieval_terms("啥是合母") == ["合母"]
    assert retrieval_terms("啥是控母") == ["控母"]
    terms = retrieval_terms("合母和控母有什么区别")
    assert "合母" in terms
    assert "控母" in terms


def test_tokenize_is_unchanged_for_stored_vectors() -> None:
    # tokenize 决定了入库向量的空间，改了会让库里既有向量与查询向量错位。
    assert tokenize("绝缘阻抗低 DC220V") == [
        "绝",
        "缘",
        "阻",
        "抗",
        "低",
        "dc220v",
    ]


def test_bigram_terms_keep_ascii_tokens_whole() -> None:
    # 英文和数字仍按连续单词切分，不被拆成两字组。
    assert "dc220v" in bigram_terms("交直流屏 DC220V")
    assert "交直" in bigram_terms("交直流屏 DC220V")


def test_retrieval_terms_falls_back_when_everything_is_filler() -> None:
    # 整句都是语气词时不能返回空，否则查询会退化成空串。
    assert retrieval_terms("是什么意思啊") != []
