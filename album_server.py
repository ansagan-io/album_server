from bottle import route, run, HTTPError, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
"""
Импортируем все необходые модуля
"""

DB_PATH = r"sqlite:///albums.sqlite3"
Base = declarative_base()


class Album(Base):
    __tablename__ = 'album'
    id = db.Column(db.INTEGER, primary_key=True)
    year = db.Column(db.INTEGER)
    artist = db.Column(db.Text)
    genre = db.Column(db.Text)
    album = db.Column(db.Text)


def connect_db():
    engine = db.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()


def find(artist):
    session = connect_db()
    albums_found = session.query(Album).filter(Album.artist == artist).all()
    return albums_found


def valid_album(album):
    """
    проверяем год на правильность то есть он должен быть int и болшьше 1900 и не менее и не больше 2020
    """
    if isinstance(album.year, int) and 2020 > album.year > 1900:

        return True
    else:
        return False


@route("/albums/<artist>")
def albums(artist):
    """
    вызывет функцию который создает лист со всеми данными о найденных альбомах.
    проверяет на наличие данных в лист если нет то поднимает требогу
    если что то есть в листе  то попытается построит из этих данных сторку и передать его на вывод
    """
    album_list = find(artist)
    if not album_list:
        message = f"No album of '{artist}' was found"
        result = HTTPError(404, message)
    else:
        result = f"<h2 style='font-family: cursive; color: darkmagenta; font-size: xx-large; margin: 30px; text-align: center; text-decoration: underline; text-decoration-style: dotted; text-decoration-color: darkgray'>{artist} has {len(album_list)} albums in existing DataBase.</h2><h3 style = 'text-align: center; font-size: x-large;font-family: cursive; color: darkmagenta'>List of {artist}'s albums:</h3>"
        album_string = ""
        i = 1  # данная переменнная нужна для нумерации албьбомов при выводе на страницу
        for album in album_list:  # разбираем лист из объектов для того что бы получить доступ ключам объектов
            album_string += f"<span style = 'color: red'>{i}.</span> <span style = 'color: darkmagenta'>'{album.album}'</span> written in <span style = 'color: red'>{album.year}</span><br>"
            i += 1
        result = result + f"<div style = 'display: block; margin: auto; text-align: center; color: blue; font-weight: bolder; font-size: unset; border: solid; width: 500; padding: 10px'>{album_string}</div>"
    return result


@route("/albums", method="POST")
def albums():
    """
    создает сессию и принимает данных об альбоме проверяет введенные данные на правильность
    если добавленный альбом от этого певца уже есть  в базе то поднимает требогу
    если введенные данные имеют не правильный тип то тоже поднимает тербогу
    если все ок объект добаляется в базу данных и ссессия закрывается
    """
    session = connect_db()
    album_to_add = Album(
        year=request.forms.get("year"),
        artist=request.forms.get("artist"),
        genre=request.forms.get("genre"),
        album=request.forms.get("album")
    )
    if not valid_album(album_to_add):
        message = f"You are trying to send inappropriate data type to Database. Please try again"
        return HTTPError(422, message)
    elif album_to_add.album in [album.album for album in find(album_to_add.artist)]:
        message = f"Album of {album_to_add.artist} named {album_to_add.album} already exist in DataBase"
        return HTTPError(409, message)
    else:
        session.add(album_to_add)
        session.commit()
        return "All data saved successfully"


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
