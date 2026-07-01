from typing import Optional

from sqlalchemy.orm import Session

from app.models.pile import ChargingPile, PileStatus, PileType
from app.models.charging import ChargingSession, SessionStatus


class PileRepo:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[ChargingPile]:
        return self.db.query(ChargingPile).all()

    def find_by_id(self, pile_id: int) -> Optional[ChargingPile]:
        return self.db.query(ChargingPile).filter(ChargingPile.id == pile_id).first()

    def find_by_type(self, pile_type: PileType) -> list[ChargingPile]:
        return self.db.query(ChargingPile).filter(ChargingPile.pile_type == pile_type).all()

    def find_online_by_type(self, pile_type: PileType) -> list[ChargingPile]:
        return self.db.query(ChargingPile).filter(
            ChargingPile.pile_type == pile_type,
            ChargingPile.status == PileStatus.ONLINE
        ).all()

    def update_status(self, pile_id: int, status: PileStatus):
        pile = self.find_by_id(pile_id)
        if pile:
            pile.status = status
            self.db.commit()

    def save(self, pile: ChargingPile) -> ChargingPile:
        self.db.add(pile)
        self.db.commit()
        self.db.refresh(pile)
        return pile

    def update(self, pile: ChargingPile):
        self.db.commit()
        self.db.refresh(pile)

    def find_active_session(self, pile_id: int) -> Optional[ChargingSession]:
        return self.db.query(ChargingSession).filter(
            ChargingSession.pile_id == pile_id,
            ChargingSession.status == SessionStatus.RUNNING
        ).first()

    def save_session(self, session: ChargingSession) -> ChargingSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_session(self, session: ChargingSession):
        self.db.commit()
        self.db.refresh(session)
