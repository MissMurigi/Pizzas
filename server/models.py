from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship: A Restaurant has many RestaurantPizzas
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')

    # Association Proxy to get Pizzas through RestaurantPizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Serialization rules to avoid deep recursion
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship: A Pizza has many RestaurantPizzas
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')

    # Association Proxy to get Restaurants through RestaurantPizzas
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Serialization rules to avoid deep recursion
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')

    # Serialization rules to avoid deep recursion
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas')

    # Validation for price between 1 and 30
    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30.")
        return value

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'