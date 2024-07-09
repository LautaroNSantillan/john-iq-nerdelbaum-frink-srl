from .entities.User import User
from werkzeug.security import check_password_hash, generate_password_hash

class ModelUser():
    @classmethod
    def login(self, db, user):
        try:
            cursor=db.connection.cursor()
            sql = "SELECT id, username, password, fullname FROM User WHERE username = %s"
            cursor.execute(sql, (user.username,))
            row=cursor.fetchone()
            if row != None:
                user=User(row[0], row[1], User.check_password(row[2], user.password), row[3] )
                return user
            else:
                return None   
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor=db.connection.cursor()
            sql = "SELECT id, username, fullname FROM User WHERE id = {}".format(id)
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2] )
            else:
                return None   
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def register(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = "INSERT INTO user (username, password, fullname) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user.username, generate_password_hash(user.password), user.fullname))
            db.connection.commit()
            return True
        except Exception as ex:
            print(ex)
            return False