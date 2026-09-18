import hashlib
import math
import re
from collections import Counter
from collections.abc import Mapping

DIMENSION = 384

# 检索时忽略的字：中文虚词、疑问词和口语语气词。
# 这些字在语料里几乎人人都出现，留着只会稀释真正实词的权重——
# 问「啥是控母」时，有效信号只有「控母」两个字，其余都是噪声。
#
# 但「常在口语句子里出现」不等于「在领域词里没信息」。一个字如果同时是虚词
# 和领域构字，一律留下：曾经把「能」当助动词剥掉，「储能」就变成了「储」；
# 把「有」剥掉，「有功」变成了「功」；把「上」「下」剥掉，「上电/下电」
# 也散了架。查询和原文对不上，检索分直接掉一档。
# 判断标准是「剥掉之后领域词会不会散架」，不是「这个字口语里常不常见」。
STOPWORDS = frozenset(
    # 虚词与连词。保留「有」——它是有功/无功/有效率的构字；
    # 保留「上」「下」「中」——分别是上电/下电、中压/中心的构字。
    "的了是在和与及或把被给对从为"
    "之其等让使由按到就都也还而但并且则"
    # 指示代词与量词
    "以于因所该此些这个们"
    # 疑问词与语气词
    "啥什么怎怎样如何哪哪里哪个哪些为啥吗呢吧啊呀么嘛喔哦唉啦咯呵哈"
    # 口语请求词。保留「要」——它是要点/重要/摘要的构字；
    # 保留「能」——它是储能/功能/性能的构字。
    "请问一告诉我想要知道解说讲看可以应该需干嘛"
    # 比较与评价
    "很太更最比较挺好的意思含义不同区别样"
)


def tokenize(text: str) -> list[str]:
    """不依赖外部模型，将中文按单字、英文和数字按连续单词切分。

    注意：入库时的向量由这个函数生成，改动它会让库里既有的向量和查询向量
    不再处于同一空间。做题级别的检索精度改进请用 `retrieval_terms`。
    """
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+", text.lower())


def bigram_terms(text: str) -> list[str]:
    """把中文按相邻两字组合，英文和数字仍按连续单词切分。

    逐字切分会丢掉词边界：「合母」和「控母」都含「母」，在单字空间里高度
    相似，分不出问的是哪一个。两字组合后「合母」「控母」各自成为独立信号，
    口语问法才不至于被无关段落挤下去。
    """
    terms: list[str] = []
    for segment in re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text.lower()):
        if not segment[0].isascii():
            if len(segment) == 1:
                terms.append(segment)
            else:
                terms.extend(segment[index : index + 2] for index in range(len(segment) - 1))
        else:
            terms.append(segment)
    return terms


def strip_stopwords(text: str) -> str:
    """去掉虚词和口语词，只留承载信息的字。"""
    return "".join(char for char in text if char not in STOPWORDS)


def retrieval_terms(text: str) -> list[str]:
    """构造查询侧的检索单元：先滤掉虚词和口语词，再做两字组合。

    滤完为空时回退到原文，避免整句都是语气词时把查询变成空串。
    """
    return bigram_terms(strip_stopwords(text) or text)


def idf_weight(document_frequency: int, total_documents: int) -> float:
    """逆文档频率：越少见的词权重越大，下限为 1，不产生负权重。

    去掉虚词还不够。剩下的实词之间差别同样很大：问「Python 怎么装环境」时，
    「装」「环」「境」在光伏语料里到处都是（设备安装、环境条件），
    命中它们并不能说明这段话在回答问题；而「合母」「绝缘阻抗」这种只出现在
    少数章节里的词，命中才算真信号。按稀有度加权，才能把两者分开。

    这个权重只用在**查询侧**的重叠计算上，不写进向量、不动库里的数据，
    因此改它不需要重新导入语料。
    """
    return math.log((total_documents + 1) / (document_frequency + 1)) + 1.0


def weighted_coverage(
    query_terms: Counter[str],
    chunk_terms: Counter[str],
    weights: Mapping[str, float],
) -> float:
    """查询词的加权覆盖率 = 命中词的权重和 ÷ 查询词的权重总和。

    分母放着查询侧全部实词的权重，所以只要有一个稀有的核心词没被命中，
    整段的重叠比例就会被明显拉下来——这正是「Python 怎么装环境」需要的效果，
    它命中的全是「装/环/境」这种到处都有的字。
    """
    total = sum(count * weights.get(term, 1.0) for term, count in query_terms.items())
    if total <= 0:
        return 0.0
    hit = sum(
        min(count, chunk_terms.get(term, 0)) * weights.get(term, 1.0)
        for term, count in query_terms.items()
    )
    return hit / total


def local_embedding(text: str, dimension: int = DIMENSION) -> list[float]:
    """生成结果稳定的哈希向量，供免费的本地开发和流程演示使用。

    这只是为了跑通 RAG 流程，并不能真正理解语义；生产环境应接入正式的
    Embedding 模型。
    """
    vector = [0.0] * dimension
    for token in tokenize(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        # 同一个词每次都会落到同一个位置，因此测试结果可重复。
        bucket = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    # 归一化后，向量点积就可以直接作为余弦相似度。
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=False))
