"""舆情数据采集服务

从多个数据源采集A股和港股的舆情数据
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import json
import time
import random


class SentimentCollector:
    """舆情数据采集器"""

    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _fetch(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """通用请求方法"""
        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.warning(f"请求失败: {url}, 状态码: {resp.status}")
        except Exception as e:
            logger.error(f"请求异常: {url}, 错误: {e}")
        return None

    async def collect_eastmoney_news(self, stock_code: str, days: int = 7) -> List[Dict]:
        """采集东方财富新闻

        Args:
            stock_code: 股票代码
            days: 采集天数
        """
        logger.info(f"开始采集东方财富新闻: {stock_code}")

        news_list = []

        # 东方财富新闻API
        base_url = "http://searchapi.eastmoney.com/api/suggest/get"

        # 获取最近新闻
        url = "http://np-api.eastmoney.com/News/GetNewsList"
        params = {
            'codes': stock_code,
            'pagesize': 50,
            'pageindex': 1,
            'date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        }

        try:
            data = await self._fetch(url, params)
            if data and 'Data' in data:
                for item in data['Data'].get('List', []):
                    news = {
                        'title': item.get('Title'),
                        'content': item.get('Digest'),
                        'url': item.get('Url'),
                        'source': 'eastmoney',
                        'published_at': self._parse_eastmoney_date(item.get('ShowTime')),
                        'collected_at': datetime.now()
                    }
                    news_list.append(news)
                    await asyncio.sleep(0.1)  # 避免请求过快

            logger.info(f"东方财富新闻采集完成: {len(news_list)} 条")
        except Exception as e:
            logger.error(f"东方财富新闻采集失败: {e}")

        return news_list

    async def collect_xueqiu_comments(self, stock_code: str, pages: int = 5) -> List[Dict]:
        """采集雪球评论

        Args:
            stock_code: 股票代码
            pages: 采集页数
        """
        logger.info(f"开始采集雪球评论: {stock_code}")

        comments_list = []

        # 雪球API
        base_url = "https://xueqiu.com/query/v1/symbol/search/status"

        # 转换股票代码格式（A股需要添加SH/SZ前缀）
        formatted_code = self._format_stock_code(stock_code)

        for page in range(1, pages + 1):
            url = f"https://xueqiu.com/statuses/search.json"
            params = {
                'symbol': formatted_code,
                'count': 20,
                'page': page
            }

            try:
                data = await self._fetch(url, params)
                if data and 'list' in data:
                    for item in data['list']:
                        comment = {
                            'stock_code': stock_code,
                            'platform': 'xueqiu',
                            'user_name': item.get('user', {}).get('screen_name'),
                            'content': item.get('description'),
                            'likes': item.get('like_count', 0),
                            'replies': item.get('reply_count', 0),
                            'created_at': self._parse_timestamp(item.get('created_at')),
                            'collected_at': datetime.now()
                        }
                        comments_list.append(comment)

                    await asyncio.sleep(0.5)  # 雪球限制更严格
            except Exception as e:
                logger.error(f"雪球评论采集失败(第{page}页): {e}")
                break

        logger.info(f"雪球评论采集完成: {len(comments_list)} 条")
        return comments_list

    async def collect_eastmoney_comments(self, stock_code: str) -> List[Dict]:
        """采集东方财富评论

        Args:
            stock_code: 股票代码
        """
        logger.info(f"开始采集东方财富评论: {stock_code}")

        comments_list = []

        # 东方财富股吧API
        url = "http://np-api.eastmoney.com/Content/GetPostList"
        params = {
            'id': stock_code,
            'pagesize': 30,
            'pageindex': 1
        }

        try:
            data = await self._fetch(url, params)
            if data and 'Data' in data:
                for item in data['Data'].get('List', []):
                    comment = {
                        'stock_code': stock_code,
                        'platform': 'eastmoney',
                        'user_name': item.get('UserName'),
                        'content': item.get('Body'),
                        'likes': item.get('LikeCount', 0),
                        'replies': item.get('ReplyCount', 0),
                        'created_at': self._parse_eastmoney_date(item.get('ShowTime')),
                        'collected_at': datetime.now()
                    }
                    comments_list.append(comment)
                    await asyncio.sleep(0.1)

            logger.info(f"东方财富评论采集完成: {len(comments_list)} 条")
        except Exception as e:
            logger.error(f"东方财富评论采集失败: {e}")

        return comments_list

    async def collect_stock_sentiment(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """采集多只股票的舆情数据

        Args:
            stock_codes: 股票代码列表

        Returns:
            {stock_code: {'news': [...], 'comments': [...]}}
        """
        results = {}

        tasks = []
        for code in stock_codes:
            tasks.extend([
                self.collect_eastmoney_news(code),
                self.collect_xueqiu_comments(code),
                self.collect_eastmoney_comments(code)
            ])

        # 并发采集
        collected = await asyncio.gather(*tasks, return_exceptions=True)

        # 整理结果
        idx = 0
        for code in stock_codes:
            results[code] = {
                'news': collected[idx] if isinstance(collected[idx], list) else [],
                'comments_xueqiu': collected[idx + 1] if isinstance(collected[idx + 1], list) else [],
                'comments_eastmoney': collected[idx + 2] if isinstance(collected[idx + 2], list) else []
            }
            idx += 3

        return results

    def _format_stock_code(self, code: str) -> str:
        """格式化股票代码（添加市场前缀）"""
        if code.startswith('6') or code.startswith('5'):
            return f'SH{code}'  # 上海交易所
        elif code.startswith('0') or code.startswith('3'):
            return f'SZ{code}'  # 深圳交易所
        elif code.startswith('00'):
            return f'HK{code}'  # 港股
        return code

    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """解析时间戳"""
        if not timestamp:
            return None
        try:
            return datetime.fromtimestamp(int(timestamp) / 1000)
        except:
            return None

    def _parse_eastmoney_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析东方财富日期格式"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                return None


async def main():
    """测试采集器"""
    collector = SentimentCollector()

    async with collector:
        # 测试采集单只股票
        results = await collector.collect_stock_sentiment(['600519', '000001', '00700'])

        for code, data in results.items():
            print(f"\n股票: {code}")
            print(f"新闻数: {len(data['news'])}")
            print(f"雪球评论数: {len(data['comments_xueqiu'])}")
            print(f"东方财富评论数: {len(data['comments_eastmoney'])}")


if __name__ == '__main__':
    asyncio.run(main())
