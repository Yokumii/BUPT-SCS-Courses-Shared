from typing import Optional

from sqlalchemy.orm import Session

from app.models.charging import ChargingRequest, QueueNumber, QueueSequence, RequestStatus, ChargingMode


class RequestRepo:
    def __init__(self, db: Session):
        self.db = db

    def save(self, request: ChargingRequest) -> ChargingRequest:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def find_by_id(self, req_id: int) -> Optional[ChargingRequest]:
        return self.db.query(ChargingRequest).filter(ChargingRequest.id == req_id).first()

    def find_by_user(self, user_id: int) -> list[ChargingRequest]:
        return self.db.query(ChargingRequest).filter(
            ChargingRequest.user_id == user_id
        ).order_by(ChargingRequest.created_at.desc()).all()

    def find_active_by_user(self, user_id: int) -> Optional[ChargingRequest]:
        return self.db.query(ChargingRequest).filter(
            ChargingRequest.user_id == user_id,
            ChargingRequest.status.in_([
                RequestStatus.WAITING,
                RequestStatus.QUEUED,
                RequestStatus.CHARGING
            ])
        ).first()

    def list_by_mode(self, mode: ChargingMode) -> list[ChargingRequest]:
        return self.db.query(ChargingRequest).filter(
            ChargingRequest.mode == mode,
            ChargingRequest.status.in_([RequestStatus.WAITING, RequestStatus.QUEUED, RequestStatus.CHARGING])
        ).order_by(ChargingRequest.created_at).all()

    def save_queue_number(self, qn: QueueNumber) -> QueueNumber:
        self.db.add(qn)
        self.db.commit()
        self.db.refresh(qn)
        return qn

    def find_queue_number_by_request(self, request_id: int) -> Optional[QueueNumber]:
        return self.db.query(QueueNumber).filter(QueueNumber.request_id == request_id).first()

    def delete_queue_number(self, qn: QueueNumber):
        self.db.delete(qn)
        self.db.commit()

    def get_next_seq(self, mode: ChargingMode) -> int:
        sequence = self.db.query(QueueSequence).filter(QueueSequence.mode == mode).first()
        if not sequence:
            max_existing = self.db.query(QueueNumber).filter(
                QueueNumber.mode == mode
            ).order_by(QueueNumber.seq.desc()).first()
            next_seq = (max_existing.seq + 1) if max_existing else 1
            sequence = QueueSequence(mode=mode, next_seq=next_seq)
            self.db.add(sequence)
            self.db.commit()
            self.db.refresh(sequence)

        current = sequence.next_seq
        sequence.next_seq += 1
        self.db.commit()
        return current

    def update(self, request: ChargingRequest):
        self.db.commit()
        self.db.refresh(request)
