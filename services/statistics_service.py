from datetime import UTC, datetime

from db.adoption import AdoptionRequest
from db.animal import Animal
from schemas.statistics import MonthlyTrend, SpeciesBreakdown, StatisticsResponse
from utils.time import utc_now


SPECIES = ("dog", "cat", "bird", "rabbit", "other")
TREND_MONTHS = 6


async def get_statistics() -> StatisticsResponse:
    total = await Animal.find().count()
    available = await Animal.find(Animal.status == "available").count()
    pending = await Animal.find(Animal.status == "pending").count()
    adopted = await Animal.find(Animal.status == "adopted").count()
    pending_requests = await AdoptionRequest.find(AdoptionRequest.status == "pending").count()

    now = utc_now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    adoptions_this_month = await AdoptionRequest.find(
        AdoptionRequest.status == "approved",
        AdoptionRequest.decided_at >= month_start,
    ).count()

    breakdown = {species: await Animal.find(Animal.species == species).count() for species in SPECIES}
    by_species = SpeciesBreakdown(**breakdown)
    trend = await _intake_vs_adoption_last_n_months(now, TREND_MONTHS)

    return StatisticsResponse(
        total_animals=total,
        available_animals=available,
        pending_animals=pending,
        adopted_animals=adopted,
        pending_requests=pending_requests,
        adoptions_this_month=adoptions_this_month,
        by_species=by_species,
        intake_vs_adoption=trend,
    )


async def _intake_vs_adoption_last_n_months(now: datetime, n: int) -> list[MonthlyTrend]:
    months = _last_n_months(now, n)
    result: list[MonthlyTrend] = []
    for start, end in months:
        intake = await Animal.find(
            Animal.arrived_at >= start,
            Animal.arrived_at < end,
        ).count()
        adoption = await AdoptionRequest.find(
            AdoptionRequest.status == "approved",
            AdoptionRequest.decided_at >= start,
            AdoptionRequest.decided_at < end,
        ).count()
        result.append(MonthlyTrend(month=start.strftime("%Y-%m"), intake=intake, adoption=adoption))
    return result


def _last_n_months(now: datetime, n: int) -> list[tuple[datetime, datetime]]:
    year, month = now.year, now.month
    pairs: list[tuple[datetime, datetime]] = []
    for _ in range(n):
        start = datetime(year, month, 1, tzinfo=UTC)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=UTC)
        else:
            end = datetime(year, month + 1, 1, tzinfo=UTC)
        pairs.append((start, end))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(pairs))
