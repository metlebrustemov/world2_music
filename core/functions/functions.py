import string
import random
from ..constants import M_EXTENTIONS

def ext_cont(file_name):
   return '.' in file_name and \
   file_name.rsplit('.', 1)[1].lower() in M_EXTENTIONS

def csrf_text(size=32, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))