"""情感分析 API 路由"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.database.models import SentimentNews, SentimentComment, SentimentTrend, SentimentKeyword
from backend.database.session import get_db
from backend.services.sentiment_collector import SentimentCollector
from backend.services.sentiment_analyzer import SentimentAnalyzer
from loguru import logger

router = APIRouter(prefix="/sentiment", tags=["舆情分析"])

analyzer = SentimentAnalyzer(method="auto")


class SentimentRequest(BaseModel):
    stock_codes: List[str]
    days: int = Query(7, description="采集天数", ge=1, le=30)


class SentimentResponse(BaseModel):
    stock_code: str
    sentiment: str  # positive, negative, neutral
    score: float
    news_count: int
    comment_count: int
    keywords: List[Dict]
    trend: List[Dict]


class SentimentDetailResponse(BaseModel):
    stock_code: str
    stock_name: Optional[str]
    overall: Dict
    news: List[Dict]
    comments: List[Dict]
    keywords: List[Dict]
    trend: List[Dict]


@router.get("/stock/{stock_code}", response_model=SentimentDetailResponse)
async def get_stock_sentiment(
    stock_code: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """获取指定股票的舆情详情"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 获取新闻数据
        news = db.query(SentimentNews).filter(
            SentimentNews.stock_code == stock_code,
            SentimentNews.collected_at >= start_date
        ).order_by(SentimentNews.published_at.desc()).limit(50).all()

        # 获取评论数据
        comments = db.query(SentimentComment).filter(
            SentimentComment.stock_code == stock_code,
            SentimentComment.collected_at >= start_date
        ).order_by(SentimentComment.created_at.desc()).limit(100).all()

        # 获取趋势数据
        trends = db.query(SentimentTrend).filter(
            SentimentTrend.stock_code == stock_code,
            SentimentTrend.date >= start_date
        ).order_by(SentimentTrend.date.desc()).limit(days).all()

        # 计算总体情感
        all_scores = []
        for n in news:
            if n.sentiment_score is not None:
                all_scores.append(n.sentiment_score)
        for c in comments:
            if c.sentiment_score is not None:
                all_scores.append(c.sentiment_score)

        overall = analyzer.aggregate_sentiments([
            {'sentiment': 'positive', 'score': s} for s in all_scores if s > 0.2
        ] + [
            {'sentiment': 'negative', 'score': s} for s in all_scores if s < -0.2
        ] + [
            {'sentiment': 'neutral', 'score': s} for s in all_scores if -0.2 <= s <= 0.2
        ])

        # 获取热门关键词
        keywords = db.query(SentimentKeyword).order_by(
            SentimentKeyword.count.desc()
        ).limit(20).all()

        return {
            "stock_code": stock_code,
            "stock_name": comments[0].stock_name if comments else None,
            "overall": overall,
            "news": [
                {
                    "title": n.title,
                    "source": n.source,
                    "sentiment": n.sentiment,
                    "sentiment_score": n.sentiment_score,
                    "published_at": n.published_at,
                    "keywords": n.keywords
                }
                for n in news
            ],
            "comments": [
                {
                    "platform": c.platform,
                    "user_name": c.user_name,
                    "content": c.content,
                    "sentiment": c.sentiment,
                    "sentiment_score": c.sentiment_score,
                    "likes": c.likes,
                    "created_at": c.created_at
                }
                for c in comments
            ],
            "keywords": [
                {
                    "word": k.keyword,
                    "count": k.count,
                    "sentiment": k.sentiment,
                    "avg_score": k.avg_score
                }
                for k in keywords
            ],
            "trend": [
                {
                    "date": t.date,
                    "avg_sentiment_score": t.avg_sentiment_score,
                    "positive_ratio": t.positive_ratio,
                    "negative_ratio": t.negative_ratio,
                    "neutral_ratio": t.neutral_ratio,
                    "volume": t.volume,
                    "keywords": t.keywords
                }
                for t in trends
            ]
        }

    except Exception as e:
        logger.error(f"获取舆情详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect")
async def collect_sentiment_data(request: SentimentRequest, db: Session = Depends(get_db)):
    """采集并分析舆情数据"""
    try:
        logger.info(f"开始采集舆情数据: {request.stock_codes}")

        # 采集数据
        collector = SentimentCollector()
        import asyncio
        results = await collector.collect_stock_sentiment(request.stock_codes)

        processed_count = 0

        # 处理每只股票的数据
        for stock_code, data in results.items():
            logger.info(f"处理股票: {stock_code}")

            # 处理新闻
            for news_data in data.get('news', []):
                # 分析情感
                sentiment_result = analyzer.analyze_text(news_data.get('title', ''))
                keywords = analyzer.extract_keywords(news_data.get('title', '') + ' ' + news_data.get('content', ''))

                # 检查是否已存在
                existing = db.query(SentimentNews).filter(
                    SentimentNews.url == news_data.get('url')
                ).first()

                if not existing:
                    news = SentimentNews(
                        stock_code=stock_code,
                        title=news_data.get('title'),
                        content=news_data.get('content'),
                        url=news_data.get('url'),
                        source=news_data.get('source'),
                        author=news_data.get('author'),
                        published_at=news_data.get('published_at'),
                        sentiment=sentiment_result['sentiment'],
                        sentiment_score=sentiment_result['score'],
                        keywords=keywords
                    )
                    db.add(news)
                    processed_count += 1

            # 处理评论（合并雪球和东方财富）
            all_comments = data.get('comments_xueqiu', []) + data.get('comments_eastmoney', [])
            for comment_data in all_comments:
                sentiment_result = analyzer.analyze_text(comment_data.get('content', ''))
                keywords = analyzer.extract_keywords(comment_data.get('content', ''))

                comment = SentimentComment(
                    stock_code=stock_code,
                    stock_name=comment_data.get('stock_name'),
                    platform=comment_data.get('platform'),
                    comment_id=comment_data.get('comment_id'),
                    user_name=comment_data.get('user_name'),
                    content=comment_data.get('content'),
                    likes=comment_data.get('likes', 0),
                    replies=comment_data.get('replies', 0),
                    created_at=comment_data.get('created_at'),
                    sentiment=sentiment_result['sentiment'],
                    sentiment_score=sentiment_result['score'],
                    keywords=keywords
                )
                db.add(comment)
                processed_count += 1

            # 更新关键词统计
            all_texts = [n.get('title', '') for n in data.get('news', [])] + \
                        [c.get('content', '') for c in all_comments]

            for text in all_texts:
                keywords = analyzer.extract_keywords(text)
                for kw in keywords:
                    keyword = db.query(SentimentKeyword).filter(
                        SentimentKeyword.keyword == kw['word']
                    ).first()

                    if keyword:
                        keyword.count += 1
                    else:
                        keyword = SentimentKeyword(
                            keyword=kw['word'],
                            count=1
                        )
                        db.add(keyword)

            # 生成趋势数据
            await _generate_trend_data(stock_code, db)

            db.commit()

        logger.info(f"舆情数据采集完成，处理 {processed_count} 条记录")

        return {
            "success": True,
            "message": f"成功采集并分析 {len(request.stock_codes)} 只股票的舆情数据",
            "processed_count": processed_count
        }

    except Exception as e:
        db.rollback()
        logger.error(f"采集舆情数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{stock_code}")
async def get_sentiment_trend(
    stock_code: str,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """获取舆情趋势数据"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trends = db.query(SentimentTrend).filter(
            SentimentTrend.stock_code == stock_code,
            SentimentTrend.date >= start_date
        ).order_by(SentimentTrend.date.asc()).all()

        return {
            "stock_code": stock_code,
            "trends": [
                {
                    "date": t.date.strftime('%Y-%m-%d'),
                    "avg_sentiment_score": t.avg_sentiment_score,
                    "positive_ratio": t.positive_ratio,
                    "negative_ratio": t.negative_ratio,
                    "neutral_ratio": t.neutral_ratio,
                    "volume": t.volume,
                    "keywords": t.keywords
                }
                for t in trends
            ]
        }

    except Exception as e:
        logger.error(f"获取舆情趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keywords/top")
async def get_top_keywords(
    limit: int = Query(20, ge=10, le=100),
    sentiment: Optional[str] = Query(None, description="情感类型: positive, negative, neutral"),
    db: Session = Depends(get_db)
):
    """获取热门关键词"""
    try:
        query = db.query(SentimentKeyword)

        if sentiment:
            query = query.filter(SentimentKeyword.sentiment == sentiment)

        keywords = query.order_by(
            SentimentKeyword.count.desc()
        ).limit(limit).all()

        return {
            "keywords": [
                {
                    "word": k.keyword,
                    "count": k.count,
                    "sentiment": k.sentiment,
                    "avg_score": k.avg_score
                }
                for k in keywords
            ]
        }

    except Exception as e:
        logger.error(f"获取热门关键词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/latest")
async def get_latest_news(
    stock_code: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = Query(20, ge=10, le=100),
    db: Session = Depends(get_db)
):
    """获取最新新闻"""
    try:
        query = db.query(SentimentNews)

        if stock_code:
            query = query.filter(SentimentNews.stock_code == stock_code)
        if sentiment:
            query = query.filter(SentimentNews.sentiment == sentiment)

        news = query.order_by(
            SentimentNews.published_at.desc()
        ).limit(limit).all()

        return {
            "news": [
                {
                    "id": n.id,
                    "stock_code": n.stock_code,
                    "title": n.title,
                    "content": n.content,
                    "source": n.source,
                    "sentiment": n.sentiment,
                    "sentiment_score": n.sentiment_score,
                    "keywords": n.keywords,
                    "published_at": n.published_at
                }
                for n in news
            ]
        }

    except Exception as e:
        logger.error(f"获取最新新闻失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_trend_data(stock_code: str, db: Session):
    """生成每日趋势数据"""
    end_date = datetime.now().date()

    # 获取最近7天的数据
    for i in range(7):
        date = end_date - timedelta(days=i)
        start_dt = datetime.combine(date, datetime.min.time())
        end_dt = datetime.combine(date, datetime.max.time())

        # 获取当日新闻
        news = db.query(SentimentNews).filter(
            SentimentNews.stock_code == stock_code,
            SentimentNews.published_at >= start_dt,
            SentimentNews.published_at <= end_dt
        ).all()

        # 获取当日评论
        comments = db.query(SentimentComment).filter(
            SentimentComment.stock_code == stock_code,
            SentimentComment.created_at >= start_dt,
            SentimentComment.created_at <= end_dt
        ).all()

        if not news and not comments:
            continue

        # 计算情感统计
        all_sentiments = []
        all_keywords = []

        for n in news:
            if n.sentiment:
                all_sentiments.append(n.sentiment)
            if n.keywords:
                all_keywords.extend(n.keywords)

        for c in comments:
            if c.sentiment:
                all_sentiments.append(c.sentiment)
            if c.keywords:
                all_keywords.extend(c.keywords)

        # 汇总统计
        total = len(all_sentiments)
        if total == 0:
            continue

        positive_count = all_sentiments.count('positive')
        negative_count = all_sentiments.count('negative')
        neutral_count = all_sentiments.count('neutral')

        # 计算平均情感分数
        scores = []
        for n in news:
            if n.sentiment_score is not None:
                scores.append(n.sentiment_score)
        for c in comments:
            if c.sentiment_score is not None:
                scores.append(c.sentiment_score)

        avg_score = sum(scores) / len(scores) if scores else 0.0

        # 聚合关键词
        keyword_counts = {}
        for kw in all_keywords:
            if isinstance(kw, dict):
                word = kw.get('word')
                if word:
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1

        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # 检查是否已存在当日数据
        existing = db.query(SentimentTrend).filter(
            SentimentTrend.stock_code == stock_code,
            SentimentTrend.date == start_dt
        ).first()

        trend_data = {
            'news_count': len(news),
            'comment_count': len(comments),
            'avg_sentiment_score': avg_score,
            'positive_ratio': positive_count / total,
            'negative_ratio': negative_count / total,
            'neutral_ratio': neutral_count / total,
            'keywords': [{'word': k, 'count': v} for k, v in top_keywords],
            'volume': len(news) * 2 + len(comments)  # 新闻权重更高
        }

        if existing:
            for key, value in trend_data.items():
                setattr(existing, key, value)
        else:
            trend = SentimentTrend(
                stock_code=stock_code,
                date=start_dt,
                **trend_data
            )
            db.add(trend)

        db.commit()
