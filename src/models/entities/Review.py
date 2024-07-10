class Review:
    def __init__(self, review_id, user_id, review_text, rating):
        self.review_id = review_id
        self.user_id = user_id
        self.review_text = review_text
        self.rating = rating

    @classmethod
    def from_form_data(cls, review_text, rating):
        review=Review(review_id=None, user_id=None, review_text=review_text, rating=rating)
        return review