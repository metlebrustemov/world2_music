from core.model.models import *

def create_database():
    if not os.path.isfile(os.getcwd()+"/core/models/{}".format(DB_NAME)): #Ve ya os.path.exists()
        db.create_all()

if __name__ == "__main__":
    print("This operation deletes your existing database files and creates new ones. \nThis means that all your data will be deleted. \nDo you want to continue? (Y, n)")
    if (input("(Yes or No)>>>").lower() == "yes"):
        create_database()
