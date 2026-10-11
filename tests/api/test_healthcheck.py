from tests.common import client

# # # # # # # # # # # # # # # # # # # # # # # # API TESTS # # # # # # # # # # # # # # # # # # # # # # # #

def test_healthcheck(): 
    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Server is running smoothly"
    }
