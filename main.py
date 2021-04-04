from flask import Flask, render_template, request, url_for, redirect
from random import choice
import playlist_builder

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html",project_title="tune fusion")

@app.route("/form")
def testpage():
  return render_template("form.html",
  page_title = "test page")

@app.route("/data", methods = ["POST"])
def data():
  username1 = request.form['username1']
  username2 = request.form['username2']
  print(username1)
  msg, rc = playlist_builder.create_joint_playlist(username1, username2, "Joint Playlist Name")
  if rc:
    print(msg)
  return redirect("/")
  #return render_template("data.html",
  #project_title = "data")

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
