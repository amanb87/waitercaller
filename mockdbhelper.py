
#  @Author: aman.buttan 
#  @Date: 2018-04-24 01:53:14 
#  @Last Modified by:   aman.buttan 
#  @Last Modified time: 2018-04-24 01:53:14 

MOCK_USERS = {'test@example.com': '123456'}

class MockDBHelper:
   
   def get_user(self, email):
      if email in MOCK_USERS:
         return MOCK_USERS[email]
      return None