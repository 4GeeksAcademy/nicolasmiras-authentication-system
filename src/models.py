from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "is_active": self.is_active,
            # do not serialize the password, its a security breach
        }



class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    diameter: Mapped[int] = mapped_column(nullable=False)
    terrain: Mapped[str] = mapped_column(nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)

    characters: Mapped[List["Character"]] = relationship(back_populates="planet")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "terrain": self.terrain,
            "population": self.population,
            # do not serialize the password, its a security breach
        }


    

class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    height: Mapped[int] = mapped_column(nullable=False)
    mass: Mapped[int] = mapped_column(nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"))
    planet: Mapped["Planet"] = relationship(back_populates="characters")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
            "favorite": self.favorite,
            # do not serialize the password, its a security breach
        }
    


class Favorite_Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    id_character: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    character: Mapped["Character"] = relationship("Character", foreign_keys=[id_character])
    user: Mapped["User"] = relationship("User", foreign_keys=[id_user])

    def serialize(self):
        return {
            "id": self.id,

            # do not serialize the password, its a security breach
        }


class Favorite_Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    id_planet: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    planet: Mapped["Character"] = relationship("Planet", foreign_keys=[id_planet])
    user: Mapped["User"] = relationship("User", foreign_keys=[id_user])

    def serialize(self):
        return {
            "id": self.id,

            # do not serialize the password, its a security breach
        }
