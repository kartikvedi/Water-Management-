from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User


class CustomerManager(BaseUserManager):

    def create_user(self, username=None, email=None, PhoneNo=None, password=None, cnic=None, name=None, NoOfBottles=0,
                    AmountDue=0, MonthlyBill=0, ):
        """
        Creates and saves a User with the given email and password.
        """
        if email is None:
            raise ValueError('Users must have an email address')
        if username is None:
            raise ValueError('Users must have an email address')
        if password is None:
            raise ValueError('Users must have a password')
        if name is None:
            raise ValueError('Users must have a name')

        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.username = username
        user_obj.email = email
        user_obj.name = name
        user_obj.cnic = cnic
        user_obj.PhoneNo = PhoneNo
        user_obj.MonthlyBill = MonthlyBill
        user_obj.NoOfBottles = NoOfBottles
        user_obj.AmountDue = AmountDue
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email, username, password, name, ):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            name=name,
            email=email,
            username=username,
            password=password
        )

        user.is_staff = True
        user.is_admin = True
        user.is_active = True
        user.is_approved = True
        user.save(using=self._db)
        return user


class UserManager(BaseUserManager):
    def create_user(self,
                    username=None,
                    email=None,
                    PhoneNo=None,
                    password=None,
                    cnic=None,
                    name=None,
                    ):
        """
        Creates and saves a User with the given email and password.
        """
        if email is None:
            raise ValueError('Users must have an email address')
        if password is None:
            raise ValueError('Users must have a password')
        if name is None:
            raise ValueError('Users must have a name')
        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.username = username
        user_obj.email = email
        user_obj.name = name
        user_obj.cnic = cnic
        user_obj.PhoneNo = PhoneNo
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_employee(self, cnic=None, PhoneNo=None, name=None, password=None, username=None, email=None):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            username=username,
            name=name,
            email=email,
            PhoneNo=PhoneNo,
        )

        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, name):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            name=name,
            email=email,
            username=username,
            password=password
        )

        user.is_staff = True
        user.is_admin = True
        user.is_active = True
        user.is_approved = True
        user.save(using=self._db)
        return user


class EmployeeManager(BaseUserManager):

    def create_user(self, username, password, phoneNo, name, email, **kwargs):
        if username is None:
            raise ValueError("Employee must have a username")
        if password is None:
            raise ValueError("Employee must have a password")
        if phoneNo is None:
            raise ValueError("Employee must have a phone no")
        if name is None:
            raise ValueError("Employee must have a name")

        user_obj = self.model(email=self.normalize_email(email), username=username, phoneNo=phoneNo, name=name,
                              **kwargs)
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, email, username, password, name):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            name=name,
            email=email,
            username=username,
            password=password
        )

        user.is_staff = True
        user.is_admin = True
        user.is_active = True
        user.is_approved = True
        user.save(using=self._db)
        return user
