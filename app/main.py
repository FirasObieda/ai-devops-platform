from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Product as ProductModel

app = FastAPI(title="E-Commerce API")

Base.metadata.create_all(bind=engine)


def getDb():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class Product(BaseModel):
    name: str
    price: float
    quantity: int

class ProductResponse(Product):
    id: int


@app.get("/")
def root():
    return {"message": "E-Commerce API is running"}


@app.get("/health")
def healthCheck():
    return {"status": "healthy"}


@app.get("/products", response_model=list[ProductResponse])
def getProducts(db: Session = Depends(getDb)):
    return db.query(ProductModel).all()

@app.get("/products/{productId}", response_model=ProductResponse)
def getProduct(productId: int, db: Session = Depends(getDb)):
    product = db.query(ProductModel).filter(
        ProductModel.id == productId
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.post("/products", response_model=ProductResponse)
def createProduct(product: Product, db: Session = Depends(getDb)):
    newProduct = ProductModel(
        name=product.name,
        price=product.price,
        quantity=product.quantity,
    )

    db.add(newProduct)
    db.commit()
    db.refresh(newProduct)

    return newProduct

 