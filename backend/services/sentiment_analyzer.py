"""情感分析服务

对采集的舆情数据进行情感分析和关键词提取
"""
import re
import jieba
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter
from loguru import logger

# 尝试导入情感分析库
try:
    from snownlp import SnowNLP
    SNOWNLP_AVAILABLE = True
except ImportError:
    SNOWNLP_AVAILABLE = False
    logger.warning("SnowNLP 未安装，将使用简单关键词分析方法")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers 未安装，无法使用FinBERT模型")


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self, method: str = "auto"):
        """
        Args:
            method: 分析方法 - 'snownlp'(中文), 'transformers'(FinBERT), 'auto'(自动选择)
        """
        self.method = method
        self.model = None
        self._init_model()

        # 情感词典
        self.positive_words = set([
            '上涨', '大涨', '暴涨', '利好', '突破', '新高', '强势', '看好',
            '买入', '推荐', '增持', '超配', '乐观', '正面', '积极', '优秀',
            '增长', '盈利', '收入', '业绩', '扩张', '收购', '合作', '创新',
            '领先', '龙头', '优质', '低估', '价值', '机会', '潜力', '反转'
        ])

        self.negative_words = set([
            '下跌', '大跌', '暴跌', '利空', '破位', '新低', '弱势', '看空',
            '卖出', '减持', '回避', '悲观', '负面', '消极', '风险', '担忧',
            '亏损', '下滑', '下降', '衰退', '收缩', '出售', '裁员', '违约',
            '债务', '危机', '崩盘', '泡沫', '高估', '套牢', '割肉', '止损',
            '调查', '处罚', '违规', '造假', '造假', '丑闻', '退市', '停牌'
        ])

    def _init_model(self):
        """初始化模型"""
        if self.method == "auto":
            if TRANSFORMERS_AVAILABLE:
                self.method = "transformers"
            elif SNOWNLP_AVAILABLE:
                self.method = "snownlp"
            else:
                self.method = "keyword"

        if self.method == "transformers":
            try:
                self.model = pipeline(
                    "text-classification",
                    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
                    return_all_scores=True
                )
                logger.info("使用 Transformers 模型进行情感分析")
            except Exception as e:
                logger.warning(f"Transformers 模型加载失败: {e}, 降级为 SnowNLP")
                self.method = "snownlp"

        if self.method == "snownlp" and SNOWNLP_AVAILABLE:
            logger.info("使用 SnowNLP 进行情感分析")

        if self.method == "keyword":
            logger.info("使用关键词匹配进行情感分析")

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        分析单条文本情感

        Returns:
            {
                'sentiment': 'positive'/'negative'/'neutral',
                'score': 0.0~1.0 (或-1~1)
            }
        """
        if not text or not text.strip():
            return {'sentiment': 'neutral', 'score': 0.0}

        text = text.strip()[:2000]  # 限制长度

        if self.method == "snownlp":
            return self._analyze_with_snownlp(text)
        elif self.method == "transformers":
            return self._analyze_with_transformers(text)
        else:
            return self._analyze_with_keywords(text)

    def _analyze_with_snownlp(self, text: str) -> Dict[str, float]:
        """使用 SnowNLP 分析"""
        try:
            s = SnowNLP(text)
            score = s.sentiments  # 0-1, 1为正向

            # 转换为 -1~1 的范围
            adjusted_score = (score - 0.5) * 2

            if adjusted_score > 0.2:
                sentiment = 'positive'
            elif adjusted_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            return {
                'sentiment': sentiment,
                'score': adjusted_score,
                'raw_score': score
            }
        except Exception as e:
            logger.error(f"SnowNLP 分析失败: {e}")
            return self._analyze_with_keywords(text)

    def _analyze_with_transformers(self, text: str) -> Dict[str, float]:
        """使用 Transformers 模型分析"""
        try:
            results = self.model(text)

            # 找到分数最高的情感类别
            scores = {item['label']: item['score'] for item in results[0]}

            # 将类别映射到我们的格式
            label_mapping = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral'
            }

            # 选择最高分的标签
            best_label = max(scores.keys(), key=lambda x: scores[x])
            best_score = scores[best_label]

            sentiment = label_mapping.get(best_label.lower(), 'neutral')

            # 转换分数为 -1~1
            if sentiment == 'positive':
                adjusted_score = best_score
            elif sentiment == 'negative':
                adjusted_score = -best_score
            else:
                adjusted_score = 0.0

            return {
                'sentiment': sentiment,
                'score': adjusted_score,
                'scores': scores
            }
        except Exception as e:
            logger.error(f"Transformers 分析失败: {e}")
            return self._analyze_with_keywords(text)

    def _analyze_with_keywords(self, text: str) -> Dict[str, float]:
        """使用关键词匹配分析"""
        positive_count = 0
        negative_count = 0

        words = jieba.lcut(text)

        for word in words:
            if word in self.positive_words:
                positive_count += 1
            elif word in self.negative_words:
                negative_count += 1

        total = positive_count + negative_count
        if total == 0:
            return {'sentiment': 'neutral', 'score': 0.0}

        # 计算分数
        if positive_count > negative_count:
            sentiment = 'positive'
            score = (positive_count - negative_count) / (positive_count + negative_count)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = -(negative_count - positive_count) / (positive_count + negative_count)
        else:
            sentiment = 'neutral'
            score = 0.0

        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': positive_count,
            'negative_count': negative_count
        }

    def extract_keywords(self, text: str, top_k: int = 10) -> List[Dict[str, float]]:
        """
        提取关键词

        Returns:
            [{'word': str, 'weight': float}]
        """
        if not text or not text.strip():
            return []

        text = text.strip()[:5000]

        try:
            # 使用 jieba 提取关键词
            words = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)

            keywords = [{'word': word, 'weight': float(weight)} for word, weight in words]
            return keywords
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, float]]:
        """批量分析文本"""
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append(result)
        return results

    def aggregate_sentiments(self, sentiment_list: List[Dict]) -> Dict:
        """
        聚合多个情感分析结果

        Returns:
            {
                'avg_score': float,
                'positive_ratio': float,
                'negative_ratio': float,
                'neutral_ratio': float,
                'positive_count': int,
                'negative_count': int,
                'neutral_count': int,
                'total_count': int
            }
        """
        if not sentiment_list:
            return {
                'avg_score': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 1.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_count': 0
            }

        total = len(sentiment_list)
        positive_count = sum(1 for s in sentiment_list if s.get('sentiment') == 'positive')
        negative_count = sum(1 for s in sentiment_list if s.get('sentiment') == 'negative')
        neutral_count = sum(1 for s in sentiment_list if s.get('sentiment') == 'neutral')

        total_score = sum(s.get('score', 0) for s in sentiment_list)
        avg_score = total_score / total if total > 0 else 0.0

        return {
            'avg_score': avg_score,
            'positive_ratio': positive_count / total,
            'negative_ratio': negative_count / total,
            'neutral_ratio': neutral_count / total,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_count': total
        }

    def aggregate_keywords(self, keyword_lists: List[List[Dict]], top_k: int = 20) -> List[Dict[str, float]]:
        """聚合多个关键词列表"""
        all_keywords = []

        for keywords in keyword_lists:
            for kw in keywords:
                all_keywords.append((kw['word'], kw['weight']))

        if not all_keywords:
            return []

        # 统计词频和权重
        counter = Counter()
        weight_sum = {}

        for word, weight in all_keywords:
            counter[word] += 1
            weight_sum[word] = weight_sum.get(word, 0) + weight

        # 计算综合权重
        result = []
        for word, count in counter.most_common(top_k):
            avg_weight = weight_sum[word] / count
            result.append({
                'word': word,
                'weight': float(avg_weight),
                'count': count
            })

        return result


def main():
    """测试情感分析"""
    analyzer = SentimentAnalyzer(method="auto")

    # 测试文本
    test_texts = [
        "贵州茅台今日大涨5%，创近期新高，市场情绪乐观",
        "某公司业绩大幅下滑，股价暴跌，投资者恐慌",
        "市场震荡整理，观望情绪浓厚"
    ]

    for text in test_texts:
        result = analyzer.analyze_text(text)
        keywords = analyzer.extract_keywords(text)

        print(f"\n文本: {text}")
        print(f"情感: {result['sentiment']}, 分数: {result['score']:.3f}")
        print(f"关键词: {[kw['word'] for kw in keywords[:5]]}")


if __name__ == '__main__':
    main()
