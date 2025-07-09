from sqlalchemy.orm import Session
from src.pedidos.pedidoModel import Pedido
from src.pedidos.pedidoSchema import PedidoSchema, PedidoUpdateSchema
from src.cliente.clienteService import get_cliente_by_id
from src.empresa.empresaService import get_empresa_by_id
from src.pedidos.detallePedido.detallePedidoModel import DetallePedido
from src.producto.prodModel import Producto


# Create a new Pedido
def create_pedido(db: Session, pedido_data: PedidoSchema):
    try:
        # Verify if the client exists
        cliente = get_cliente_by_id(db, pedido_data.cliente_id)
        if not cliente:
            raise ValueError("El cliente especificado no existe.")

        # Verify if the company exists
        empresa = get_empresa_by_id(db, pedido_data.empresa_id)
        if not empresa:
            raise ValueError("La empresa especificada no existe.")

        # Initialize total for the pedido
        total_pedido = 0
        detalles_pedido = []

        # Process each detalle in the pedido
        for detalle_data in pedido_data.detalles_pedido:
            producto = (
                db.query(Producto)
                .filter(Producto.id == detalle_data["producto_id"])
                .first()
            )
            if not producto:
                raise ValueError(
                    f"El producto con ID {detalle_data['producto_id']} no existe."
                )
            # Get the unit price of the product discount if applicable
            precio_unitario = producto.precio
            if producto.descuento:
                descuento = producto.descuento
            total_detalle = detalle_data["cantidad"] * precio_unitario
            total_pedido += total_detalle

            detalle_pedido = DetallePedido(
                producto_id=detalle_data["producto_id"],
                cantidad=detalle_data["cantidad"],
                precio_unitario=precio_unitario,
                descuento=descuento,
                total=total_detalle,
            )
            detalles_pedido.append(detalle_pedido)

        # Create the pedido
        pedido = Pedido(
            cliente_id=pedido_data.cliente_id,
            empresa_id=pedido_data.empresa_id,
            estado="pendiente",
            total=total_pedido,
            observaciones=pedido_data.observaciones,
        )
        db.add(pedido)
        db.commit()
        db.refresh(pedido)

        # Add detalles to the pedido
        for detalle in detalles_pedido:
            detalle.pedido_id = pedido.id
            db.add(detalle)

        db.commit()

        # Convert Pedido object to dictionary
        pedido_dict = {
            "id": pedido.id,
            "cliente_id": pedido.cliente_id,
            "empresa_id": pedido.empresa_id,
            "estado": pedido.estado,
            "fecha_creacion": pedido.fecha_creacion,
            "fecha_actualizacion": pedido.fecha_actualizacion,
            "fecha_vencimiento": pedido.fecha_vencimiento,
            "total": float(pedido.total) if pedido.total else None,
            "observaciones": pedido.observaciones,
        }

        # Convert DetallePedido objects to dictionaries
        detalles_dict = [
            {
                "id": detalle.id,
                "producto_id": detalle.producto_id,
                "cantidad": detalle.cantidad,
                "precio_unitario": float(detalle.precio_unitario),
                "descuento": float(detalle.descuento) if detalle.descuento else None,
                "total": float(detalle.total),
            }
            for detalle in detalles_pedido
        ]

        # Include detalles_pedido in the response
        pedido_dict["detalles_pedido"] = detalles_dict

        return pedido_dict

    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al crear el pedido: {str(e)}")


# Get a Pedido by ID
def get_pedido_by_id(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        return {"error": "Pedido no encontrado"}

    detalles_pedido = (
        db.query(DetallePedido).filter(DetallePedido.pedido_id == pedido_id).all()
    )

    # Convert Pedido and DetallePedido objects to dictionaries
    pedido_dict = {
        "id": pedido.id,
        "cliente_id": pedido.cliente_id,
        "empresa_id": pedido.empresa_id,
        "estado": pedido.estado,
        "fecha_creacion": pedido.fecha_creacion,
        "fecha_actualizacion": pedido.fecha_actualizacion,
        "fecha_vencimiento": pedido.fecha_vencimiento,
        "total": float(pedido.total) if pedido.total else None,
        "observaciones": pedido.observaciones,
    }

    detalles_dict = [
        {
            "id": detalle.id,
            "producto_id": detalle.producto_id,
            "cantidad": detalle.cantidad,
            "precio_unitario": float(detalle.precio_unitario),
            "descuento": float(detalle.descuento) if detalle.descuento else None,
            "total": float(detalle.total),
        }
        for detalle in detalles_pedido
    ]

    return {"pedido": pedido_dict, "detalles_pedido": detalles_dict}


# Ready for conversion
def get_ready_for_conversion(db: Session):
    try:
        pedidos = db.query(Pedido).filter(Pedido.estado == "Pendiente").all()
        return {"pedidos": pedidos}
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al obtener pedidos listos para conversión: {str(e)}")


# Convert a Pedido
def convert_pedido(db: Session, pedido_id: int):
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}

        # Update the estado to "Convertido"
        pedido.estado = "Convertido"
        db.commit()
        db.refresh(pedido)

        return {"message": "Pedido convertido exitosamente", "pedido": pedido}

    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al convertir el pedido: {str(e)}")


# Update a Pedido
def update_pedido(db: Session, pedido_id: int, pedido_data: PedidoUpdateSchema):
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            return {"error": "Pedido no encontrado"}

        # Update basic fields
        for key, value in pedido_data.dict(exclude_unset=True).items():
            if key != "detalles_pedido":  # Skip detalles_pedido for now
                setattr(pedido, key, value)

        # Handle detalles_pedido updates
        if hasattr(pedido_data, "detalles_pedido") and pedido_data.detalles_pedido:
            total_pedido = 0
            db.query(DetallePedido).filter(
                DetallePedido.pedido_id == pedido_id
            ).delete()

            for detalle_data in pedido_data.detalles_pedido:
                producto = (
                    db.query(Producto)
                    .filter(Producto.id == detalle_data.producto_id)
                    .first()
                )
                if not producto:
                    raise ValueError(
                        f"El producto con ID {detalle_data.producto_id} no existe."
                    )

                precio_unitario = producto.precio
                total_detalle = detalle_data.cantidad * precio_unitario
                total_pedido += total_detalle

                detalle_pedido = DetallePedido(
                    pedido_id=pedido_id,
                    producto_id=detalle_data.producto_id,
                    cantidad=detalle_data.cantidad,
                    precio_unitario=precio_unitario,
                    total=total_detalle,
                )
                db.add(detalle_pedido)

            pedido.total = total_pedido

        db.commit()
        db.refresh(pedido)
        return pedido

    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al actualizar el pedido: {str(e)}")


# # Delete a Pedido
# def delete_pedido(db: Session, pedido_id: int):
#     pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
#     if pedido:
#         db.delete(pedido)
#         db.commit()
#     return pedido
