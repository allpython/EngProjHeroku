import unittest
from app import app, db, json, Client, Product

class AppTestCase(unittest.TestCase):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True
    app.login_manager.init_app(app)

    def setUp(self):
        self.client = app.test_client()
        #self._login()

    def tearDown(self):
        """teardown all initialized variables."""
        print("tearing down")

    def test_01_test_index(self):
        res = self.client.get('/', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_02_product_api_post(self):
        product = Product.query.all()
        counter = len(product)
        jsonStr = {"list":[{"productArea": "testProduct"}]}
        res = self.client.post('/api/v1/product/save',
                              data=json.dumps(jsonStr),
                              content_type='application/json')
        final_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(final_response['status'], 200)
        self.assertEqual(len(final_response['messages']), 0)

        product_after_insert = Product.query.all()
        self.assertEqual(len(product_after_insert), counter+1)

    def test_03_products_api_get_all(self):
        res = self.client.get('/api/v1/products')
        cust_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(cust_response['status'], 200)
        self.assertGreater(cust_response['total'], 0)

    def test_04_product_api_delete_wrong(self):
        res = self.client.get('/api/v1/product/delete/120')
        self.assertEqual(res.status_code, 404)

    def test_05_product_delete(self):
        product = Product.query.filter_by(product_area="testProduct").first()
        self.assertIsNotNone(product)

        res = self.client.get('/api/v1/product/delete/'+ str(product.id))
        cust_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(cust_response['status'], 200)

        product_after_delete = Product.query.filter_by(product_area="testProduct").first()
        self.assertIsNone(product_after_delete)

    def test_06_client_api_post(self):
        client = Client.query.all()
        counter = len(client)

        jsonStr = {"list":[{"clientName": "testClient"}]}
        res = self.client.post('/api/v1/client/save',
                              data=json.dumps(jsonStr),
                              content_type='application/json')
        final_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(final_response['status'], 200)
        self.assertEqual(len(final_response['messages']), 0)

        client_after_insert = Client.query.all()
        self.assertEqual(len(client_after_insert), counter+1)

    def test_07_clients_api_get_all(self):
        res = self.client.get('/api/v1/clients')
        cust_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(cust_response['status'], 200)
        self.assertGreater(cust_response['total'], 0)

    def test_08_client_api_delete_wrong(self):
        res = self.client.get('/api/v1/client/delete/120')
        self.assertEqual(res.status_code, 404)


    def test_09_client_delete(self):
        client = Client.query.filter_by(client_name="testClient").first()
        self.assertIsNotNone(client)
        res = self.client.get('/api/v1/client/delete/'+ str(client.id))
        cust_response = json.loads(res.data.decode('utf-8'))
        self.assertEqual(cust_response['status'], 200)

        client = Client.query.filter_by(client_name="test").first()
        self.assertIsNone(client)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
