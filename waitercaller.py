/*
 * @Author: aman.buttan 
 * @Date: 2018-04-24 01:22:20 
 * @Last Modified by: aman.buttan
 * @Last Modified time: 2018-04-24 01:22:45
 */
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
   return "Under construction"

if __name__ == '__main__':
    app.run(port=5000, debug=True)