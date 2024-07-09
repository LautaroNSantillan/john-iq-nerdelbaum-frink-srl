from .entities.User import User

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
                print(row[1],"------------", row[2],"------------", user.password)
                return user
            else:
                return None   
        except Exception as ex:
            raise Exception(ex)