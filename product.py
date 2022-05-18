"""
This file contains Product class.
"""


class Product:
    """
    Creates a product with the attributes' id, name, price, qty, warehouse
    === Public Attributes ===
    product_id: Unique id assigned to every product
    product_name: The name of the product
    product_price: Price of the product in dollars ($)
    product_qty: Total qty available at all locations'
    product_warehouse: Dictionary of locations the product is stored along with
    the available qty at those locations.
    """

    product_id: int
    product_name: str
    product_price: float
    product_qty: int
    product_warehouse: dict

    def __init__(self, product_id: int, product_name: str,
                 product_price: float):

        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price
        self.product_qty = 0
        self.product_warehouse = {}


