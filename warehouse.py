"""
This file contains Warehouse class.
"""


class Warehouse:
    """
    Creates a warehouse with the attributes' id, name, address, products,
    total_qty
    === Public Attributes ===
    warehouse_id: Unique id assigned to every warehouse
    warehouse_name: The name of the warehouse
    warehouse_address: Address of the warehouse
    warehouse_products: Dictionary of products stored along with
    the available qty.
    warehouse_qty: Total number of products at the warehouse
    """

    warehouse_id: int
    warehouse_name: str
    warehouse_address: str
    warehouse_products: dict
    warehouse_qty: int

    def __init__(self, warehouse_id: int, warehouse_name: str,
                 warehouse_address: str):
        """
        Initializes a warehouse

        :param warehouse_id: Warehouse ID
        :param warehouse_name: Warehouse Name
        :param warehouse_address: Warehouse Address
        """
        self.warehouse_id = warehouse_id
        self.warehouse_name = warehouse_name
        self.warehouse_address = warehouse_address
        self.warehouse_qty = 0
        self.warehouse_products = {}

    def addProduct(self, product_id: int, qty: int):
        """
        Adds product to existing warehouse

        :param product_id: Product ID
        :param qty: Qty being added to the warehouse
        :return: None
        """
        self.warehouse_products[product_id] = qty
        self.warehouse_qty += qty
