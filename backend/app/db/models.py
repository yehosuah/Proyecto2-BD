from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


id_bigint = BigInteger().with_variant(Integer, "sqlite")
id_uuid = Uuid(as_uuid=False).with_variant(String(36), "sqlite")


class Base(DeclarativeBase):
    pass


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(id_bigint, primary_key=True, autoincrement=True)
    id_rol: Mapped[int] = mapped_column(SmallInteger, ForeignKey("rol.id_rol"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class SesionUsuario(Base):
    __tablename__ = "sesion_usuario"

    id_sesion: Mapped[str] = mapped_column(id_uuid, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(id_bigint, ForeignKey("usuario.id_usuario"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    creada_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    expira_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revocada_en: Mapped[datetime | None] = mapped_column(DateTime)


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria: Mapped[int] = mapped_column(id_bigint, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Proveedor(Base):
    __tablename__ = "proveedor"

    id_proveedor: Mapped[int] = mapped_column(id_bigint, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    contacto: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255))
    telefono: Mapped[str | None] = mapped_column(String(30))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Producto(Base):
    __tablename__ = "producto"

    id_producto: Mapped[int] = mapped_column(id_bigint, primary_key=True, autoincrement=True)
    id_categoria: Mapped[int] = mapped_column(id_bigint, ForeignKey("categoria.id_categoria"), nullable=False)
    id_proveedor: Mapped[int | None] = mapped_column(id_bigint, ForeignKey("proveedor.id_proveedor"))
    sku: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id_detalle_pedido: Mapped[int] = mapped_column(id_bigint, primary_key=True, autoincrement=True)
    id_pedido: Mapped[int] = mapped_column(id_bigint, nullable=False)
    id_producto: Mapped[int] = mapped_column(id_bigint, ForeignKey("producto.id_producto"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
