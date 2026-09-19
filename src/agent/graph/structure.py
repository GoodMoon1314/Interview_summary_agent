from typing import TypedDict, Annotated, Literal, List
from pydantic import BaseModel, Field
from typing import List


# 定义结构化

# 用户需求
class UserDemand(BaseModel):
    demand: Annotated[str, "用户需求知识点"]
    is_rule: Annotated[bool, "用户输入是否合规,Ture:合规 False:不合规"]


# 面试题整理
class QAItem(BaseModel):
    problem: str
    answer: str


class ProblemList(BaseModel):
    problem_list: Annotated[List[QAItem], "面试问题及答案列表，每个元素包含problem、answer两个字段"]


# 面试题审查
class ProblemReview(BaseModel):
    score: int = Field(ge=0, le=10, description="分数，取值范围0~10")
    review: Annotated[str, "审核内容"]


# 长记忆存储格式
class LangMemory(BaseModel):
    total_score: Annotated[str, "用户综合得分,将所有题目的得分相加"]
    score_full_mark: Annotated[str, "本次答题满分分数,每道题目10分,将所有题目的分数相加"]
    overall_summary: Annotated[str, "用户的综合评价,总结"]
    strengths: Annotated[str, "用户擅长方面"]
    weak_points: Annotated[str, "用户薄弱方面"]
    suggestions: Annotated[str, "建议用户增强方面"]
