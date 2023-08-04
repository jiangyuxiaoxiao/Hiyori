"""
@Author: Ame lian
@Github: https://github.com/AmeNeri
@Date: 2023/8/2-17:32
@Desc: 
@Ver : 1.0.0
"""
from nonebot.internal.rule import Rule

def rule(game=None) -> Rule:
    async def _rule() -> bool:
        return True

    return Rule(_rule)

