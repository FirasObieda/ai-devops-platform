def testGetProducts(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


def testCreateProduct(client):
    newProduct = {
        "name": "Mouse",
        "price": 100.0,
        "quantity": 10,
    }

    response = client.post("/products", json=newProduct)

    assert response.status_code == 200
    assert response.json()["name"] == "Mouse"
    assert response.json()["price"] == 100.0
    assert response.json()["quantity"] == 10


def testGetExistingProduct(client):
    newProduct = {
        "name": "Laptop",
        "price": 3500.0,
        "quantity": 10,
    }

    createResponse = client.post("/products", json=newProduct)

    productId = createResponse.json()["id"]

    response = client.get(f"/products/{productId}")

    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"


def testGetNonexistentProduct(client):
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"