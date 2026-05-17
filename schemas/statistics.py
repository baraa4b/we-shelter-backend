from schemas.common import BaseSchema


class SpeciesBreakdown(BaseSchema):
    dog: int = 0
    cat: int = 0
    bird: int = 0
    rabbit: int = 0
    other: int = 0


class MonthlyTrend(BaseSchema):
    month: str
    intake: int
    adoption: int


class StatisticsResponse(BaseSchema):
    total_animals: int
    available_animals: int
    pending_animals: int
    adopted_animals: int
    pending_requests: int
    adoptions_this_month: int
    by_species: SpeciesBreakdown
    intake_vs_adoption: list[MonthlyTrend]
