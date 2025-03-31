import pytest
from counter.entrypoints.webapp import create_app
from io import BytesIO

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_object_count_endpoint(client):
    # Prepare test image clearly
    with open('resources/images/cat.jpg', 'rb') as image_file:
        data = {
            'file': (BytesIO(image_file.read()), 'cat.jpg'),
            'threshold': '0.5',
            'model_name': 'model_a'
        }

    # Send POST request clearly to the endpoint
    response = client.post('/object-count', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    json_resp = response.get_json()
    
    # Verify response structure clearly
    assert 'counts' in json_resp
    assert isinstance(json_resp['total'], int)
