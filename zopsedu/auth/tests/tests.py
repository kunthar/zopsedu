"""Authentication Tests"""
import unittest

from zopsedu.app import DB
from zopsedu.lib.test import ZopseduTestCase
from zopsedu.auth.models.auth import User


class AuthTestCase(ZopseduTestCase):
    """Authentication Test Sınıfı"""
    def test_signup_login_logout(self):
        """
        Kullanıcı kayıt, login ve logout işlemlerini test eden sınıftır.
        """
        self.signup()
        self.login()
        self.logout()
        self.delete_user()

    def signup(self):
        """
        Yeni kullanıcı kaydeden test metodu.

        Signup view'unu get yaparak çağırır. Dönen formu post eder.
        `test` kullanıcı adı ve parolasıyla veritabanına kaydeder.

        """
        resp = self.client.get('/auth/signup')
        self.assert200(resp)
        resp = self.client.post(
            '/auth/signup',
            data=dict(username='test', password='test')
        )
        # signup sonrası login sayfasına yönledireceği için
        self.assert_status(resp, status_code=302)

    def login(self):
        """

        Var olan kullanıcıyı sisteme login eden test metodu.

        Login view'unu get yaparak çağırır. Dönen formu post eder.
        `test` kullanıcı adı ve parolasıyla kullanıcıyı doğrular.

        """
        resp = self.client.get('/auth/login')
        self.assert200(resp)
        resp = self.client.post(
            '/auth/login',
            data=dict(username='test', password='test')
        )
        # login sonrası bir sayfaya yönlendirileceği için
        self.assert_status(resp, status_code=302)

    def logout(self):
        """
        Login olmuş kullanıcıyı logout eden metottur.

        Logout view'una get isteği yaparak kullanıcıyı logout eder.

        """
        resp = self.client.get('/auth/logout')
        self.assert_status(resp, status_code=302)

    @staticmethod
    def delete_user():
        """
        Register edilen test kullanıcısını veritabanından silen metottur.

        """
        user = DB.session.query(User).filter_by(username='test').first()
        DB.session.delete(user)
        DB.session.commit()


if __name__ == '__main__':
    unittest.main()
