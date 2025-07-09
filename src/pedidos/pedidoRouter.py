from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.pedidos.pedidoService import create_pedido, get_pedido_by_id, update_pedido
from src.pedidos.pedidoSchema import PedidoSchema, PedidoUpdateSchema
from database import get_db

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

# Create a new Pedido
@router.post("/", response_model=dict)
def create_pedido_endpoint(pedido_data: PedidoSchema, db: Session = Depends(get_db)):
    try:
        pedido = create_pedido(db, pedido_data)
        return {"message": "Pedido creado exitosamente", "pedido": pedido}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get a Pedido by ID
@router.get("/{pedido_id}", response_model=dict)
def get_pedido_endpoint(pedido_id: int, db: Session = Depends(get_db)):
    pedido = get_pedido_by_id(db, pedido_id)
    if not pedido:
        return {"error": "Pedido no encontrado"}  # Ensure response is a valid dictionary
    return {"pedido": pedido}

# Update a Pedido
@router.put("/{pedido_id}", response_model=dict)
def update_pedido_endpoint(pedido_id: int, pedido_data: PedidoUpdateSchema, db: Session = Depends(get_db)):
    try:
        pedido = update_pedido(db, pedido_id, pedido_data)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return {"message": "Pedido actualizado exitosamente", "pedido": pedido}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# # Delete a Pedido
# @router.delete("/{pedido_id}", response_model=dict)
# def delete_pedido_endpoint(pedido_id: int, db: Session = Depends(get_db)):
#     pedido = delete_pedido(db, pedido_id)
#     if not pedido:
#         raise HTTPException(status_code=404, detail="Pedido no encontrado")
#     return {"message": "Pedido eliminado exitosamente"}