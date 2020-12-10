import bcrypt
from models import database, PartsOfSpeech, Translations, Users
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.from_pyfile("config.py")


if __name__ == "__main__":
    app.run()


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(_):
    if not database.is_closed():
        database.close()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    name = request.form["name"]
    mail = request.form["mail"]
    password = hash_password(request.form["password"].encode("utf-8"))
    Users.insert(name=name, mail=mail, password=password, role_id=1).execute()
    return redirect(url_for("login"))


@app.route("/")
def start():
    return redirect(url_for("register"))


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    mail = request.form["mail"]
    if mail is None:
        return render_template("login_failed.html", message='לא הוכנס דוא"ל!')
    user = Users.select().where(Users.mail == mail).get()
    if not user:
        return render_template("login_failed.html", message="המשתמש אינו קיים!")
    password = request.form["password"].encode("utf-8")
    if bcrypt.checkpw(password, str(user.password).encode("utf-8")):
        session["mail"] = user.mail
        session["name"] = user.name
        session["role"] = user.role_id
        return redirect(url_for("search"))
    return render_template("login_failed.html", message="שם משתמש או סיסמה אינם נכונים")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    for item in ("mail", "name", "role"):
        session.pop(item, None)
    return redirect(url_for("register"))


@app.route("/search")
def search():
    word = request.args.get("word")
    if not word:
        return render_template("search.html", role=session["role"])
    word = word.lower()
    translations = get_translation(word)
    if len(translations) == 0:
        translations = None
    else:
        translations = [(t.translation, t.part_of_speech.name, t.explanation) for t in translations]
    return render_template("search.html",
                           word=word,
                           translations=translations,
                           role=session["role"])


def get_translation(word):
    word = word.lower()
    query = Translations.select().where((Translations.word == word) & (Translations.confirmed == 1))
    results = [result for result in query]
    return results


@app.route("/upload", methods=["GET", "POST"])
def add_word():
    if request.method == "GET":
        return render_template("upload.html", parts=get_parts_dict().values())
    word = request.form["word"].lower()
    translation = request.form["translation"]
    part_id = get_parts_dict(name_to_id=True)[request.form["parts_of_speech"]]
    explanation = request.form["explanation"]
    if not explanation:
        explanation = None
    Translations.insert(word=word,
                        translation=translation,
                        updated_by=session["mail"],
                        part_of_speech_id=part_id,
                        explanation=explanation,
                        confirmed=False).execute()
    return redirect(url_for("search"))


def get_parts_dict(name_to_id=False):
    query = PartsOfSpeech.select()
    if name_to_id:
        results = [(result.name, result.id) for result in query]
    else:
        results = [(result.id, result.name) for result in query]
    return dict(results)


@app.route("/check")
def check_words():
    words = [(t.word, t.translation, t.part_of_speech.name, t.explanation) for t in words_to_confirm()]
    return render_template("check.html", words=words)


@app.route("/confirm/<word>/<translation>", methods=["GET", "POST"])
def confirm_word(word, translation):
    Translations.update({Translations.confirmed: True}).where(
        (Translations.word == word) and (Translations.translation == translation)).execute()
    return redirect(url_for("check_words"))


@app.route("/delete/<word>/<translation>", methods=["GET", "POST"])
def delete_word(word, translation):
    value = Translations.select().where((Translations.word == word) and (Translations.translation == translation)).get()
    value.delete_instance()
    return redirect(url_for("check_words"))


def words_to_confirm():
    query = Translations.select().where(Translations.confirmed == 0)
    results = [result for result in query]
    return results


# a = get_translation("interpretação")
# for i in a:
#     print(i.word, i.translation, i.part_of_speech_id, i.explanation, i.confirmed)
# print("-" * 50)
# add_word(word="interpretação", translation="פרשנות", part_of_speech="שם עצם")
# a = get_translation("interpretação")
# for i in a:
#     print(i.word, i.translation, i.part_of_speech_id, i.explanation, i.confirmed)
# print(words_to_confirm())
# print("-" * 50)
# confirm_word(word="interpretação", translation="פרשנות")
# a = get_translation("interpretação")
# for i in a:
#     print(i.word, i.translation, i.part_of_speech_id, i.explanation, i.confirmed)




# def get_songs(artist_id):
#     resp = requests.get(f"http://theaudiodb.com/api/v1/json/1/mvid.php?i={artist_id}").json()
#     songs = {(song["strTrack"], song["strMusicVid"]) for song in resp["mvids"]}
#     songs = list(songs)
#     random.shuffle(songs)
#     return songs[:DISPLAY_SONGS]
#
#
# @app.route("/<artist_name>/pictures")
# def pictures(artist_name):
#     resp = requests.get(f"http://theaudiodb.com/api/v1/json/1/search.php?s={artist_name}")
#     details = resp.json()["artists"][0]
#     images = []
#     for item in IMAGES_KEYS:
#         images.append(details[item])
#     return render_template("pictures.html",
#                            logo=details["strArtistLogo"],
#                            banner=details["strArtistBanner"],
#                            name=artist_name,
#                            images=images)
