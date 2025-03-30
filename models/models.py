from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str
    base_salary: float = 0
    bonus: float = 0


class PositionResponse(BaseModel):
    name: str
    levels: list[dict]


class DependencyCreate(BaseModel):
    from_position: str
    from_level: int
    to_position: str
    to_level: int
    formula_salary: str
    formula_bonus: str


class SalaryCalculationResponse(BaseModel):
    results: dict