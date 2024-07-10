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
        
    @classmethod
    def update_user_info(cls, db, id, new_fullname=None, new_username=None):
        try:
            cursor = db.connection.cursor()
            
            # Check if the new username already exists
            if new_username:
                cursor.execute("SELECT * FROM user WHERE username = %s", (new_username,))
                existing_user = cursor.fetchone()
                if existing_user:
                    return False, "Username already exists."

            # Build the SQL update statement
            sql = "UPDATE user SET "
            updates = []
            params = []

            if new_fullname:
                updates.append("fullname = %s")
                params.append(new_fullname)
            
            if new_username:
                updates.append("username = %s")
                params.append(new_username)

            if not updates:
                return False, "No updates provided."

            sql += ", ".join(updates)
            sql += " WHERE id = %s"
            params.append(id)

            cursor.execute(sql, params)
            db.connection.commit()
            cursor.close()
            return True, "User information updated successfully."
        except Exception as ex:
            print(f"Error updating user info: {ex}")
            db.connection.rollback()
            return False, str(ex)