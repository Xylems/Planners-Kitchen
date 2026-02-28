from datetime import UTC, datetime

from pydantic import UUID4
from sqlalchemy import select

from mealie.db.models.household.pantry import PantryItem
from mealie.schema.household.pantry import PantryItemCreate, PantryItemRead, PantryItemUpdate

from .repository_generic import HouseholdRepositoryGeneric


class RepositoryPantry(HouseholdRepositoryGeneric[PantryItemRead, PantryItem]):
    def get_by_location(self, location: str) -> list[PantryItemRead]:
        stmt = (
            select(self.model)
            .filter(self.model.household_id == self.household_id)
            .filter(self.model.location == location)
        )
        return [self.schema.model_validate(r) for r in self.session.execute(stmt).scalars().all()]

    def get_by_food_id(self, food_id: UUID4) -> list[PantryItemRead]:
        stmt = (
            select(self.model)
            .filter(self.model.household_id == self.household_id)
            .filter(self.model.food_id == str(food_id))
        )
        return [self.schema.model_validate(r) for r in self.session.execute(stmt).scalars().all()]

    def mark_depleted(self, food_id: UUID4, status: str, quantity: float | None = None) -> None:
        """Mark pantry items with given food_id as low or out, optionally updating quantity."""
        items = self.get_by_food_id(food_id)
        for item in items:
            db_item = self.session.get(self.model, str(item.id))
            if db_item:
                if status == "out":
                    db_item.is_out = True
                    db_item.is_low = True
                elif status == "low":
                    db_item.is_low = True
                    db_item.is_out = False
                else:
                    db_item.is_low = False
                    db_item.is_out = False
                if quantity is not None:
                    db_item.quantity = quantity
                db_item.last_updated = datetime.now(UTC)
        self.session.commit()
