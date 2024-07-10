from models.entities.Company import Company

class ModelCompany:
    @classmethod
    def create_company(self, db, company):
        try:
            cursor = db.connection.cursor()
            sql = "INSERT INTO company (name, img, location) VALUES (%s, %s, %s)"
            cursor.execute(sql, (company.name, company.img, company.location))
            db.connection.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def get_all_companies(self, db):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT name, img, location FROM company"
            cursor.execute(sql)
            rows = cursor.fetchall()
            companies = []
            for row in rows:
                companies.append(Company(row[0], row[1], row[2]))
            return companies
        except Exception as ex:
            raise Exception(ex)

