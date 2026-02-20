"""Entidades de dominio para gestión de minutas."""

from dataclasses import dataclass


@dataclass(slots=True)
class Jardin:
    id: int
    nombre: str
    direccion: str | None = None


@dataclass(slots=True)
class Alimento:
    id: int
    nombre: str
    unidad: str = "g"
    activo: bool = True


@dataclass(slots=True)
class Minuta:
    id: int
    jardin_id: int
    nombre: str
    fecha: str | None = None


@dataclass(slots=True)
class MinutaItem:
    id: int
    minuta_id: int
    alimento_id: int
    cantidad_gramos: float
