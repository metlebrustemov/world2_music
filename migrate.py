from core.model.models import *

def create_database():
    if not os.path.isfile(os.getcwd()+"/core/models/{}".format(DB_NAME)): #Ve ya os.path.exists()
        db.create_all()

if __name__ == "__main__":
    create_database()