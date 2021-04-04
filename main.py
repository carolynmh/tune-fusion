from flask import Flask, render_template, request, url_for, redirect
from random import choice
import playlist_builder

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html",project_title="tune fusion")

@app.route("/usernames")
def usernames():
  return render_template("usernames.html", page_title = "Gathering data...")

@app.route("/data", methods = ["POST"])
def data():
  username1 = request.form['username1']
  username2 = request.form['username2']
  msg, rc = playlist_builder.create_joint_playlist(
        [username1, username2], "")
  if rc:
    print(msg)
  else:
    # msg is a playlist
    return render_template("playlist_v2.html", playlist=msg[0], name=msg[1])  
  return redirect("/")

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
