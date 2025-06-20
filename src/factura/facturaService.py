from sqlalchemy.orm import Session
from src.factura.facModel import Factura
from src.factura.facturaSchema import FacturaSchema, FacturaUpdateSchema


def get_all_facturas(db: Session):
    return db.query(Factura).all()


def get_factura_by_id(db: Session, factura_id: int):
    return db.query(Factura).filter(Factura.id == factura_id).first()


def get_or_create_factura(db: Session, factura_data: FacturaSchema):
    factura = (
        db.query(Factura)
        .filter(Factura.operaciones == factura_data.operaciones)
        .first()
    )
    if not factura:
        factura = Factura(**factura_data.model_dump())
        db.add(factura)
        db.commit()
        db.refresh(factura)
    return factura


def update_factura(db: Session, factura_id: int, factura_data: FacturaUpdateSchema):
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if factura:
        for key, value in factura_data.model_dump(exclude_unset=True).items():
            setattr(factura, key, value)
        db.commit()
        db.refresh(factura)
    return factura


# def delete_factura(db: Session, factura_id: int):
#     factura = db.query(Factura).filter(Factura.id == factura_id).first()
#     if factura:
#         db.delete(factura)
#         db.commit()
#     return factura
