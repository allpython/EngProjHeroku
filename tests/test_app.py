import unittest
from project import app, db
from project.models import Client, Product, User
#from flask_login import current_user

class AppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("creating databases")
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        print("destroying all")
        db.drop_all()

    def setUp(self):
        self.client = app.test_client()
        #self._login()

    def test_01_test_index(self):
        res = self.client.get('/', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
