from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from werkzeug.exceptions import BadRequest
from flask import make_response, jsonify
import datetime

# Create the application
app = Flask(__name__)

# Create the API
api = Api(app)

# Create the database and database connection
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


# Create the product model
class ProductModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=True)
    sku = db.Column(db.String(255), unique=True, nullable=False)
    images = db.Column(db.JSON(), nullable=True)
    video_link = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float(2), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=True)

    def __repr__(self):
        return f"Product(sku={self.sku})"

    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


# Create the products resource
class Products(Resource):
    def post(self):
        products_post_args = reqparse.RequestParser()
        products_post_args.add_argument(
            "title", type=str, required=True, help="Product title is required"
        )
        products_post_args.add_argument("description", type=str, required=False)
        products_post_args.add_argument("sku", type=str, required=True)
        products_post_args.add_argument(
            "images", type=str, required=False, action="append"
        )
        products_post_args.add_argument("video_link", type=str, required=False)
        products_post_args.add_argument("price", type=float, required=True)
        products_post_args.add_argument("quantity", type=int, required=False)

        try:
            args = products_post_args.parse_args()
            try:
                product = ProductModel(
                    title=args["title"],
                    description=args["description"],
                    sku=args["sku"],
                    images=args["images"],
                    video_link=args["video_link"],
                    price=args["price"],
                    quantity=args["quantity"],
                    created_at=datetime.datetime.now(),
                )
                db.session.add(product)
                db.session.commit()

                return make_response(jsonify(product.as_dict()), 201)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"An error occurred: {e._message}"}), 500
                )
        except BadRequest as e:
            return make_response(jsonify({"error": e.description}), e.code)

    def get(self):
        products = ProductModel.query.all()
        products_as_json = [product.as_dict() for product in products]
        return make_response(jsonify(products_as_json), 200)


class Product(Resource):
    def get(self, product_id):
        product = ProductModel.query.filter_by(id=product_id).first()
        if not product:
            return make_response(
                jsonify({"error": f"Product with ID {product_id} not found"}), 404
            )
        return make_response(jsonify(product.as_dict()), 200)

    def put(self, product_id):
        product_put_args = reqparse.RequestParser()
        product_put_args.add_argument(
            "title", type=str, required=True, help="Product title is required"
        )
        product_put_args.add_argument("description", type=str, required=False)
        product_put_args.add_argument("sku", type=str, required=True)
        product_put_args.add_argument(
            "images", type=str, required=False, action="append"
        )
        product_put_args.add_argument("video_link", type=str, required=False)
        product_put_args.add_argument("price", type=float, required=True)
        product_put_args.add_argument("quantity", type=int, required=False)

        try:
            args = product_put_args.parse_args()
            try:
                product = ProductModel.query.filter_by(id=product_id).first()
                if not product:
                    return make_response(
                        jsonify({"error": f"Product with ID {product_id} not found"}),
                        404,
                    )
                else:
                    for arg in args:
                        if arg in product.__table__.columns:
                            setattr(product, arg, args[arg])
                    product.updated_at = datetime.datetime.now()
                    db.session.add(product)
                    db.session.commit()
                    return make_response(jsonify(product.as_dict()), 201)
            except Exception as e:
                return make_response(
                    jsonify({"error": f"An error occurred: {e._message}"}), 500
                )
        except BadRequest as e:
            return make_response(jsonify({"error": e.description}), e.code)

    def delete(self, product_id):
        if not ProductModel.query.filter_by(id=product_id).first():
            return make_response(
                jsonify({"error": f"Product with ID {product_id} not found"}), 404
            )

        ProductModel.query.filter_by(id=product_id).delete()
        db.session.commit()
        return make_response(
            jsonify({"message": f"Product with ID {product_id} deleted successfully"}),
            200,
        )


api.add_resource(Products, "/api/products")
api.add_resource(Product, "/api/products/<int:product_id>")
