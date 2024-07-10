from .entities.Review import Review
from flask_login import current_user


class ModelReview:
    @classmethod
    def create_review(cls, db, review):
        try:
            cursor = db.connection.cursor()
            sql = "INSERT INTO review (user_id, review_text, rating) VALUES (%s, %s, %s)"
            cursor.execute(sql, (current_user.id, review.review_text, review.rating))
            db.connection.commit()
            cursor.close()  
            return True
        except Exception as ex:
            print(f"Error creating review: {ex}")
            db.connection.rollback()
            return False
        

    @classmethod
    def update_review(cls, db, review_id, new_review_text=None, new_rating=None):
        try:
            cursor = db.connection.cursor()
            sql = "UPDATE review SET "
            updates = []
            params = []

            if new_review_text is not None:
                updates.append("review_text = %s")
                params.append(new_review_text)

            if new_rating is not None:
                updates.append("rating = %s")
                params.append(new_rating)

            if not updates:
                return False, "No updates provided."

            sql += ", ".join(updates)
            sql += " WHERE review_id = %s AND user_id = %s AND disabled = FALSE"
            params.extend([review_id, current_user.id])


            cursor.execute(sql, params)
            db.connection.commit()
            cursor.close()
            return True, "Review updated successfully."
        except Exception as ex:
            print(f"Error updating review: {ex}")
            db.connection.rollback()
            return False, f"Error updating review: {ex}"


        
    @classmethod
    def get_review_by_user_id(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT * FROM review WHERE user_id = %s AND disabled = FALSE"
            cursor.execute(sql, (user_id,))
            review = cursor.fetchone()
            cursor.close()
            if review:
                return Review(review_id=review[0], user_id=review[1], review_text=review[2], rating=review[3])
            return None
        except Exception as ex:
            print(f"Error fetching review: {ex}")
            return None
        

    
    @classmethod
    def disable_review(cls, db, review_id):
        try:
            cursor = db.connection.cursor()
            sql = "UPDATE review SET disabled = TRUE WHERE review_id = %s AND user_id = %s"
            params = (review_id, current_user.id)
            
            cursor.execute(sql, params)
            db.connection.commit()
            cursor.close()
            return True, "Review disabled successfully."
        except Exception as ex:
            print(f"Error disabling review: {ex}")
            db.connection.rollback()
            return False, f"Error disabling review: {ex}"
